import ctypes,os,platform
import sys,librosa
from ctypes import *
from formatConvert import pcm2wav
import numpy as np
import sys,os
from os import  path
sys.path.append('../')
from commFunction import get_data_array,make_out_file
from VAD_NN.hubconf import silero_vad
from PCC.Pearson_CC import get_max_cc_by_dll


import numpy as np



def merge_intervals(intervals, N):
    new_intervals = []
    for i in range(len(intervals)):
        a, b = intervals[i][0], intervals[i][1]
        if i == 0:
            continue
        if i == 1:
            new_intervals.append([0, (intervals[i][0] + intervals[i - 1][1]) // 2])
        else:
            new_intervals.append([(intervals[i-1][0]+intervals[i-2][1])//2+1, (intervals[i-1][1]+intervals[i][0])//2])
    new_intervals.append([(intervals[-2][1] + intervals[-1][0]) // 2 + 1, N - 1])
    return new_intervals

def shift_array_by_interval(arr, intervals, offsets):
    """
    对numpy数组按照多个区间和偏移进行重新排列顺序
    参数：
        arr: 一维numpy数组
        intervals: 区间列表，格式为[[start1, end1], [start2, end2], ...]
        offsets: 偏移列表，格式为[offset1, offset2, ...]
    返回值：
        排序后的新数组
    """
    if offsets >= 0:
        base_point = intervals[0] - offsets
        arr1 = arr[:base_point]
        arr2 = arr[intervals[0]:]
        arr3 = arr[base_point:intervals[0]]
        new_arr = np.concatenate((arr1, arr2, arr3))
    if offsets <= 0:
        base_point = intervals[0] - offsets
        arr1 = arr[:intervals[0]]
        arr2 = arr[intervals[0]:base_point]
        arr3 = arr[intervals[0]:]
        new_arr = np.concatenate((arr1, arr2, arr3))
    # 返回新数组
    return new_arr






def replace_none(arr):
    """
    将数组arr中的None元素替换为周围两个元素的平均值
    参数：
        arr: 一维数组，包含None和数字元素
    返回值：
        替换后的新数组
    """
    n = len(arr)
    result = []

    if all(x is None for x in arr):
        result = None
    else:
        val = arr[0] if arr[0] is not None else arr[1]
        for i in range(n):
            if arr[i] is None:
                if i == n - 1 or arr[i + 1] is None:
                    val = val
                else:
                    k = i + 1
                    while k < n and arr[k] is None:
                        k += 1
                    if k == n:
                        val = val
                    elif k == i + 1:
                        val = arr[k]
                    else:
                        val = (arr[i - 1] + arr[k]) / 2
            else:
                val = arr[i]
            result.append(val)
            val = val if arr[i] is None else arr[i]
    return result

def shift_array(arr, n):
    """
    将数组arr中的前n个元素补到最后
    参数：
        arr: 一维numpy数组
        n: 指定的元素数量
    返回值：
        补全前n个元素后的新数组
    """
    # 使用切片语法将数组分为前n个元素和从第n个元素开始的元素
    arr1 = arr[:n]
    arr2 = arr[n:]
    # 使用concatenate函数拼接数组
    new_arr = np.concatenate((arr2, arr1))
    # 返回新数组
    return new_arr

def get_my_dll():
    """
    :return:
    """
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/pcc.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/pcc.dylib')
    if cur_paltform == 'Linux':
        mydll = CDLL(sys.prefix + '/pcc.so')
    return mydll

def cal_fine_delay_of_specific_section(reffile, testfile,speech_section=None,targetfs=8000,outfile=None):
    """"""
    if speech_section is None:
        speech_section = silero_vad(reffile)
        #speech_section = [[0.941, 3.712], [4.7, 7.5]]
    delaysearchRange = 4
    delayThreshhold = 0.3
    single_frame_size = 0.5
    frameshift = 0.4
    ref_orgin_data,fs,ch = get_data_array(reffile)
    test_orgin_data,fs,ch = get_data_array(testfile)
    refdata = librosa.resample(ref_orgin_data.astype(np.float32), orig_sr=fs ,target_sr=targetfs)

    testdata = librosa.resample(test_orgin_data.astype(np.float32), orig_sr=fs ,target_sr=targetfs)
    maxsearchlen = len(testdata)
    delay_list = []
    int_intervers =  [[int(x*fs) for x in inner_arr] for inner_arr in speech_section]

    for point in speech_section:

        startpoint,endpoint = int(point[0]*targetfs),int(point[1]*targetfs)
        cal_len = endpoint - startpoint
        last_start_point,last_end_point = startpoint,endpoint
        caltimes = (cal_len - (single_frame_size) * targetfs) // (frameshift * targetfs)
        caltimes = int(caltimes)
        assert  caltimes > 0
        cc_list = []
        for times in range(caltimes):
            start = int(startpoint + times * frameshift * targetfs)
            srcblock = refdata[start:start + int(single_frame_size*targetfs)]
            limit = min(maxsearchlen,int(start+(single_frame_size+delaysearchRange)*targetfs))
            dstbloack = testdata[start:limit]
            maxCoin, startPoint = get_max_cc_by_dll(srcblock, dstbloack, get_my_dll(), 1)

            if maxCoin > delayThreshhold:
                cc_list.append(round((startPoint / targetfs), 8))
        if len(cc_list) == 0:
            curDealy = None
        else:
            curDealy = sum(cc_list)/len(cc_list)
        delay_list.append(curDealy)
    delay_list = replace_none(delay_list)

    if delay_list is None:
        return None
    delay_list = [int(x*fs) for x in delay_list]

    result = [delay_list[0]]
    prev = delay_list[0]
    for i in range(1, len(delay_list)):
        diff = delay_list[i] - prev
        result.append(diff)
        prev = delay_list[i]


    base = shift_array(test_orgin_data, result[0])
    if len(delay_list) == 1:
        if outfile is not None:
            make_out_file(outfile, base, fs, ch)
        return sum(delay_list) / len(delay_list) / fs
    intervals = merge_intervals(int_intervers,len(test_orgin_data))

    for i in range(len(result)):
        if i == 0:
            continue
        else:
            base = shift_array_by_interval(base,intervals[i],result[i])


    if outfile is not None:
        make_out_file(outfile, base, fs, ch)

    if len(delay_list) == 0:
        return  None
    else:
        return sum(delay_list)/len(delay_list)/fs



def cal_fine_delay(reffile, testfile,targetfs=8000,outfile=None):
    """"""
    delaysearchRange = 4
    delayThreshhold = 0.5
    single_frame_size = 2
    blank_duraition = 0.5
    reforgindata,fs,ch = get_data_array(reffile)
    testorigndata,fs,ch = get_data_array(testfile)
    refdata = librosa.resample(reforgindata.astype(np.float32), orig_sr=fs ,target_sr=targetfs)

    testdata = librosa.resample(testorigndata.astype(np.float32), orig_sr=fs ,target_sr=targetfs)


    cal_len = min(len(refdata),len(testdata)) - blank_duraition*2* targetfs

    caltimes = (cal_len - (delaysearchRange + single_frame_size) * targetfs) // (single_frame_size * targetfs)
    caltimes = int(caltimes)
    assert  caltimes > 0
    cc_list = []
    for times in range(caltimes):
        start = int(times * single_frame_size * targetfs + blank_duraition*targetfs)
        offset = int(single_frame_size*targetfs)
        srcblock = refdata[start:start + offset]
        dstbloack = testdata[start-offset:start-offset + (single_frame_size+delaysearchRange)*targetfs]
        maxCoin, startPoint = get_max_cc_by_dll(srcblock, dstbloack, get_my_dll(), 1)
        print(maxCoin,startPoint)
        if maxCoin > delayThreshhold:
            cc_list.append(round((startPoint / targetfs), 8))
    print(cc_list)
    if len(cc_list) == 0:
        return  None
    else:
        finaldelay = sum(cc_list)/len(cc_list)
        if outfile is not None:
            make_out_file(outfile,shift_array(testorigndata,int(fs*finaldelay)),fs,ch)
        return finaldelay


if __name__ == '__main__':
       ref = 'speech_cn.wav'
       test = 'mixDstFile_minus_13.wav'
       test2 = 'mixFile.wav'
       #a = cal_fine_delay_of_specific_section(pcm2wav(ref),pcm2wav(test),outfile='out.wav',speech_section=([16.467,18.769],[19.6,21.2],[22,24.2]))
       a = cal_fine_delay_of_specific_section(pcm2wav(ref), pcm2wav(test), outfile='out2.wav')
       #b = cal_fine_delay(pcm2wav(ref),pcm2wav(test2))
       #a = cal_fine_delay(pcm2wav(ref), pcm2wav(test),outfile='out.wav')
       print(a)
       pass