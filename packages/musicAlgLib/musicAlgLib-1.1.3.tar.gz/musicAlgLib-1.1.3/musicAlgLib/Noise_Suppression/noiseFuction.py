# -*- coding: utf-8 -*-
import copy
import sys,os
from os import  path

sys.path.append(os.path.dirname(path.dirname(__file__)))

from commFunction import get_rms,make_out_file,get_ave_rms,get_peak_rms
import numpy as np

from SNR_ESTIMATION.MATCH_SIG import match_sig
from timeAligment.time_align import cal_fine_delay_of_specific_section,cal_fine_delay
from commFunction import get_data_array
import scipy.signal as sg

speechSection = [12, 15]
noiseSection = [0, 10]
FRAME_LEN = 9600
frame_shift = 4800

import statistics

def subtract_overlap(A, B):
    result = []
    i, j = 0, 0
    while i < len(A) and j < len(B):
        if A[i][1] < B[j][0]:
            result.append(A[i])
            i += 1
        elif A[i][0] > B[j][1]:
            j += 1
        else:
            if A[i][0] < B[j][0]:
                result.append([A[i][0], B[j][0]])
            if A[i][1] > B[j][1]:
                A[i][0] = B[j][1]
                j += 1
            else:
                i += 1

    while i < len(A):
        result.append(A[i])
        i += 1

    return result

def find_overlap(A, B):
    result = []
    i, j = 0, 0
    while i < len(A) and j < len(B):
        if A[i][1] >= B[j][0] and B[j][1] >= A[i][0]:
            overlap_start = max(A[i][0], B[j][0])
            overlap_end = min(A[i][1], B[j][1])
            result.append([overlap_start, overlap_end])

        if A[i][1] < B[j][1]:
            i += 1
        elif A[i][1] > B[j][1]:
            j += 1
        else:
            i += 1
            j += 1

    return result

def calculate_statistics(arr):
    # 过滤掉数组中的None元素
    arr = [x for x in arr if x is not None]
    # 计算平均值
    mean = statistics.mean(arr)
    # 计算标准差
    stdev = statistics.stdev(arr)
    return mean, stdev


def get_maxima(values:np.ndarray):
    """极大值"""
    max_index = sg.argrelmax(values)[0]
    return max_index,values[max_index]

def get_minima(values:np.ndarray):
    """极小值"""
    min_index = sg.argrelmin(values)[0]
    return min_index,values[min_index]


def get_data_pairs(srcFile=None,testFile=None):
    """
    Parameters
    ----------
    srcFile
    testFile
    Returns
    -------
    """


    #samples = match_sig(refFile=srcFile, testFile=testFile)
    samples = cal_fine_delay_of_specific_section(srcFile, testFile, speech_section=[[12.3,14.5]], targetfs=8000, outfile=None)
    if samples is None:
        return  None
    dataSrc, fs, chn = get_data_array(srcFile)
    dataTest, fs2, chn2 = get_data_array(testFile)

    print(dataTest,dataSrc,samples)
    assert fs == fs2
    assert  chn2 == chn
    assert samples > 0

    dataTest = dataTest[int(samples*fs):]
    M,N = len(dataSrc),len(dataTest)
    targetLen = min(M,N)
    return dataSrc[:targetLen],dataTest[:targetLen],fs,chn


def cal_noise_converge(dataSrc,dataTest,fs,chn):
    """
    Parameters
    ----------
    dataSrc
    dataTest
    Returns
    -------
    """
    srcSpeechLevel = get_rms(dataSrc[fs*speechSection[0]:fs*speechSection[1]])
    curSpeechLevel = get_rms(dataTest[fs*speechSection[0]:fs*speechSection[1]])

    # log（V1 / V2) = X/20

    gain = np.power(10,(srcSpeechLevel - curSpeechLevel)/20)
    newData = dataTest.astype(np.float32) * gain
    make_out_file('source.wav', dataSrc.astype(np.int16), fs, chn)
    make_out_file('target.wav',newData.astype(np.int16),fs,chn)

    n_sengen = len(newData) // FRAME_LEN
    MAX_RMS = -120
    for a in range(n_sengen):
        curLevel = get_rms(newData[a*FRAME_LEN:(a+1)*FRAME_LEN])
        print(MAX_RMS,curLevel)
        if curLevel > MAX_RMS:
            MAX_RMS = curLevel
        if curLevel < MAX_RMS - 12:
            break
    converge = a * FRAME_LEN / fs
    if converge >= noiseSection[1]:
        nsLevel = 0.0
    else:
        nsLevel = get_ave_rms(dataSrc[int(converge * fs) :noiseSection[1]* fs]) - get_ave_rms(newData[int(converge * fs) :noiseSection[1]* fs])
    return converge, nsLevel
    #TODO 收敛时间
    #TODO 降噪量

def cal_speech_floor(section,realData,fs):
    start = int(fs * section[0])
    end = int(fs * section[1])
    return get_rms(realData[start:end])

def cal_level_drop_in_sections(sections,srcdata,AdjustData,fs):
    level = []
    for subsection in sections:
        start = int(fs * subsection[0])
        end = int(fs*subsection[1])
        if end - start < fs * 0.01:
            continue
        cursrcArray = srcdata[start:end]
        cursrcLevel = get_rms(cursrcArray)
        curdataArray  = AdjustData[start:end]
        curdstLevel = get_rms(curdataArray)

        curdiv = curdstLevel - cursrcLevel
        level.append(curdiv)
    return sum(level)/len(level)

def cal_transient_noise_Supp_by_ref(srcFile,testFile,speechSection,musicMode=False,noisetype='beat'):
    """
    :return:
    """

    timeDict = {'beat': 25412, "break": 27215, "cafe": 38683, 'clap': 25245, 'creak': 24025, "hammer_strike": 12355,
                'keyboard': 21086, 'knock': 9743, 'knock_iron_door': 25397, 'nature': 48000, 'strike': 13103,
                'strike_2': 12906, 'thunder': 19200, 'tones': 7769}
    noise = timeDict[noisetype]/48000
    pause = 2* timeDict[noisetype]/48000
    std_len = 960
    speechListInTran = []

    if musicMode:
        before_point = 13
        end_point = 32
        timeduration = 33
    else:
        before_point = 13
        end_point = 26.5
        timeduration = 27

    n = int(timeduration//(noise+pause))

    for i in range(n):
        speechListInTran.append([i*(noise+pause), i*(noise+pause)+noise])
    extra = timeduration - (noise+pause)*n

    lastPoint = speechListInTran[-1][1]+pause
    if extra > 0:
        minextra = min(extra,noise)

        speechListInTran.append([lastPoint,lastPoint+minextra])

    speechListInTran = find_overlap(speechListInTran,[[0,end_point]])

    overlap = find_overlap(speechSection,speechListInTran)

    speechSectioncopy = copy.deepcopy(speechSection)
    nonoverlap = subtract_overlap(speechSectioncopy,speechListInTran)


    speechSectioncopy = copy.deepcopy(speechListInTran)
    noisenonoverlap = subtract_overlap(speechSectioncopy,speechSection)


    noisenonoverlap = find_overlap(noisenonoverlap,[[0,end_point]])



    srcdata, fs, ch = get_data_array(srcFile)
    testdata, fs, ch = get_data_array(testFile)
    FRAME_LEN = fs*1
    cal_level = 999
    # 计算录音文件和原始文件的差，做补偿
    for singleSection in nonoverlap:
        start = int(fs*singleSection[0])
        end = int(fs*singleSection[1])
        curPeakSrc = get_peak_rms(srcdata[start:end])
        curPeakDst = get_peak_rms(testdata[start:end])
        curdiv =curPeakSrc - curPeakDst
        if cal_level > curdiv:
            cal_level = curdiv
    factor = 10 ** (cal_level / 20)
    AdjustTestData = testdata * factor
    AdjustTestData = AdjustTestData.astype(np.int16)

    speechstartPoint = speechSection[0][0]
    speechendPoint = speechSection[-1][1]

    initSections = find_overlap(speechListInTran,[[0,2]])

    init_Level = cal_level_drop_in_sections(initSections,srcdata,AdjustTestData,fs)

    beoreSections = find_overlap(speechListInTran,[[before_point,speechstartPoint]])


    before_speech_level = cal_level_drop_in_sections(beoreSections,srcdata,AdjustTestData,fs)

    afterSections = find_overlap(speechListInTran, [[speechendPoint, end_point]])

    after_speech_level = cal_level_drop_in_sections(afterSections, srcdata, AdjustTestData, fs)

    betweenSections = []
    print(speechListInTran)
    for i in range(len(speechSection)):
        if i == 0:
            continue
        cursection = find_overlap(speechListInTran,[[speechSection[i-1][1],speechSection[i][0]]])
        print(cursection)
        betweenSections = betweenSections + cursection
    print(betweenSections)
    try:
        between_speech_level = cal_level_drop_in_sections(betweenSections, srcdata, AdjustTestData, fs)
    except:
        between_speech_level = None


    in_speech_level = cal_level_drop_in_sections(overlap, srcdata, AdjustTestData, fs)


    before_speech_floor = cal_speech_floor([before_point,speechstartPoint],testdata,fs)



    std_sample_list = []
    std_sample_list_src = []

    noiseConcernSection = beoreSections + betweenSections + afterSections


    for subection in noiseConcernSection:
        start = subection[0]
        end = subection[1]
        if start == end:
            continue
        cursrcArray = srcdata[int(start*fs):int(end*fs)]
        cursrcLevel = get_rms(cursrcArray)
        curdataArray  = AdjustTestData[int(start*fs):int(end*fs)]
        curdstLevel = get_rms(curdataArray)
        currealArray = testdata[int(start*fs):int(end*fs)]
        curdstlevel_real = get_rms(currealArray)
        curdiv = curdstLevel - cursrcLevel

        sub_n_sgen = len(currealArray)//std_len
        for b in range(sub_n_sgen):
            subdataarray = currealArray[b*std_len:b*std_len+std_len]
            subsrcdataarray = cursrcArray[b*std_len:b*std_len+std_len]
            std_sample_list.append(get_rms(subdataarray))
            std_sample_list_src.append(get_rms(subsrcdataarray))


    for subection in noisenonoverlap:
        start = subection[0]
        end = subection[1]
        cursrcLevel = get_rms(srcdata[int(start*fs):int(end*fs)])
        curdstLevel = get_rms(AdjustTestData[int(start*fs):int(end*fs)])
        curdiv = curdstLevel - cursrcLevel
        if curdiv < init_Level - 6:
            break
    converage = subection[0]

    if init_Level - before_speech_level < 3:
        if before_speech_floor < -65:
            converage = 0.0

    post_std = np.std(std_sample_list, ddof=1) - np.std(std_sample_list_src, ddof=1)
    noise_floor = sum(std_sample_list)/len(std_sample_list)
    print(init_Level,before_speech_level,after_speech_level,in_speech_level,between_speech_level,before_speech_floor,converage,post_std,noise_floor)


    mean,stdev =calculate_statistics([before_speech_level,after_speech_level,between_speech_level])

    return converage, mean, stdev, in_speech_level, post_std, noise_floor
    #return converage, before_speech_level, after_speech_level, in_speech_level, between_speech_level, post_std,noise_floor

def cal_noise_Supp_by_ref(srcFile,testFile,speechSection,musicMode=False):
    """
    :return:
    """
    FRAME_LEN = 9600
    frame_shift = 4800
    std_len = 960
    if musicMode:
        before_point = 13
        end_point = 32
    else:
        before_point = 13
        end_point = 26.5


    srcdata, fs, ch = get_data_array(srcFile)
    testdata, fs, ch = get_data_array(testFile)
    cal_level = 999
    # 计算录音文件和原始文件的差，做补偿
    for singleSection in speechSection:
        start = int(fs*singleSection[0])
        end = int(fs*singleSection[1])
        curPeakSrc = get_peak_rms(srcdata[start:end])
        curPeakDst = get_peak_rms(testdata[start:end])
        curdiv =curPeakSrc -curPeakDst
        if cal_level > curdiv:
            cal_level = curdiv

    factor = 10 ** (cal_level / 20)
    AdjustTestData = testdata * factor
    AdjustTestData = AdjustTestData.astype(np.int16)
    print(cal_level,'level')

    n_sengen = (len(srcdata) - FRAME_LEN) // frame_shift

    startPoint = speechSection[0][0]
    endPoint = speechSection[-1][1]

    init_Level,init_cnt = 0,0
    before_speech_level,before_sppech_cnt = 0,0
    before_speech_floor = 0
    after_speech_level, after_sppech_cnt = 0, 0
    in_speech_level,in_speech_cnt = 0,0
    between_speech_level,bwtween_speech_cnt = 0,0
    convert_index = 0
    std_sample_list = []
    std_sample_list_src = []
    for a in range(n_sengen):
        cursrcArray = srcdata[a * frame_shift:a * frame_shift + FRAME_LEN]
        cursrcLevel = get_rms(cursrcArray)
        curdataArray  = AdjustTestData[a * frame_shift:a * frame_shift + FRAME_LEN]
        curdstLevel = get_rms(curdataArray)
        currealArray = testdata[a * frame_shift:a * frame_shift + FRAME_LEN]
        curdstlevel_real = get_rms(currealArray)
        curdiv = curdstLevel - cursrcLevel
        print(curdstLevel,cursrcLevel)
        if (a * frame_shift) > before_point * fs and (a * frame_shift) + FRAME_LEN < startPoint*fs:
            #std_sample_list.append(curdstlevel_real)
            sub_n_sgen = len(currealArray)//std_len
            for b in range(sub_n_sgen):
                subdataarray = currealArray[b*std_len:b*std_len+std_len]
                subsrcdataarray = cursrcArray[b*std_len:b*std_len+std_len]
                std_sample_list.append(get_rms(subdataarray))
                std_sample_list_src.append(get_rms(subsrcdataarray))
        if (a * frame_shift) > endPoint * fs and (a * frame_shift) + FRAME_LEN < end_point*fs:
            #std_sample_list.append(curdstlevel_real)
            sub_n_sgen = len(currealArray)//std_len
            for b in range(sub_n_sgen):
                subdataarray = currealArray[b*std_len:b*std_len+std_len]
                subsrcdataarray = cursrcArray[b * std_len:b * std_len + std_len]
                std_sample_list.append(get_rms(subdataarray))
                std_sample_list_src.append(get_rms(subsrcdataarray))
        if a >= 1 and a <= 3:
            init_Level += curdiv
            init_cnt += 1
        if (a * frame_shift) > (startPoint-1) * fs and (a * frame_shift) + FRAME_LEN < startPoint*fs:
            before_speech_level += curdiv
            before_speech_floor += curdstlevel_real
            before_sppech_cnt += 1
        if (a * frame_shift) > (endPoint) * fs:
            after_speech_level += curdiv
            after_sppech_cnt += 1
        for scnt in speechSection:
            if (a * frame_shift) > scnt[0] * fs and (a * frame_shift) + FRAME_LEN < scnt[1] * fs:
                in_speech_level += curdiv
                in_speech_cnt += 1
        if len(speechSection) > 1:
            for i,scnt in enumerate(speechSection):
                if i == 0:
                    continue
                if (a * frame_shift) > speechSection[i-1][1] * fs and (a * frame_shift) + FRAME_LEN < \
                        speechSection[i][0] * fs:
                    between_speech_level += curdiv
                    bwtween_speech_cnt += 1
    init_Level = init_Level/init_cnt
    before_speech_level = before_speech_level/before_sppech_cnt
    after_speech_level = after_speech_level/after_sppech_cnt
    in_speech_level = in_speech_level/in_speech_cnt
    before_speech_floor = before_speech_floor/before_sppech_cnt

    if bwtween_speech_cnt != 0:
        between_speech_level = between_speech_level/bwtween_speech_cnt
    else:
        between_speech_level = None

    for a in range(n_sengen):
        cursrcLevel = get_rms(srcdata[a * frame_shift:a * frame_shift + FRAME_LEN])
        curdstLevel = get_rms(AdjustTestData[a * frame_shift:a * frame_shift + FRAME_LEN])
        curdiv = curdstLevel - cursrcLevel
        print(curdiv)
        if a >= 1 and curdiv < init_Level - 6:
            break
    converage = (a * frame_shift)/fs
    print(before_speech_floor)
    print(converage)
    if init_Level - before_speech_level < 3:
        if before_speech_floor < -65:
            converage = 0.0

    post_std = np.std(std_sample_list, ddof=1) - np.std(std_sample_list_src, ddof=1)
    noise_floor = sum(std_sample_list)/len(std_sample_list)
    print(init_Level,before_speech_level,after_speech_level,in_speech_level,between_speech_level,before_speech_floor,converage,post_std,noise_floor)

    mean,stdev =calculate_statistics([before_speech_level,after_speech_level,between_speech_level])
    print()
    return converage, mean, stdev, in_speech_level, post_std, noise_floor


    #return converage, before_speech_level, after_speech_level, in_speech_level, between_speech_level, post_std,noise_floor

def cal_noise_Supp(srcFile,testFile,nslabmode=False,start=0.2,end=15.8,noiseType='None'):
    """
    Parameters
    ----------
    data
    Returns
    -------
    """
    nosieVariable = {'bubble': 4, 'car': 4.5, 'restaurant': 7,'white':3,'traffic':4,'metro':3.5,'None':4}

    if nslabmode:
        #确定计算边界
        dataSrc, fs, chn = get_data_array(testFile)
        overallLen = len(dataSrc)
        lowTmp,upperTmp = 0,overallLen
        if start is None or start < 0.1:
            dataFloor = dataSrc[0:int(0.1*fs)]
            Floor = get_rms(dataFloor)

        else:
            #  计算src noise
            lowTmp = int(start * fs)
            dataFloor = dataSrc[0:lowTmp]
            Floor = get_rms(dataFloor)

        if end is None:
            dataDegrad = dataSrc[overallLen-fs:overallLen]
        else:
            upperTmp = int(end*fs)
            dataDegrad = dataSrc[int((end-2)*fs):upperTmp]
        Degrad = get_rms(dataDegrad)

        # 计算rms求最大值
        dataSrc = dataSrc[lowTmp:upperTmp]
        datanew = dataSrc.astype(np.float32)
        n_sengen = (len(datanew)-FRAME_LEN)//frame_shift
        MAX_RMS,maxindex,MIN_RMS,minindex = -120,0,0,0
        index = 0
        x,y = [],[]
        for a in range(n_sengen):
            index += 1
            curLevel = get_rms(datanew[a * frame_shift:a * frame_shift + FRAME_LEN])
            if curLevel > MAX_RMS:
                MAX_RMS = curLevel
                maxindex = index
            x.append(index*frame_shift/fs)
            y.append(curLevel)
        # 找到第一个拐点
        for i,curlel in enumerate(y):
            if i < maxindex:
                continue
            else:
                if curlel < MAX_RMS - nosieVariable[noiseType]/2-3:
                    break
        firindex = i
        firstconvertime = (i) * frame_shift / fs

        #计算先验噪声
        lastindex = (len(datanew) - 2 * fs)/frame_shift
        post = y[int(lastindex):]

        pre_std = np.std(post, ddof=1)

        #计算最小值
        index = 0
        for a in range(n_sengen):
            index += 1
            curLevel = get_rms(datanew[a * frame_shift:a * frame_shift + FRAME_LEN])
            if curLevel < MIN_RMS and index > firindex:
                MIN_RMS = curLevel
                minindex = index
        # 求极小值
        minimadex,minmavalue = get_minima(np.array(y))
        for a in range (len(minimadex)):
            if minmavalue[a] < MIN_RMS + 2 and minimadex[a] < minindex:
                MIN_RMS = minmavalue[a]
                minindex = minimadex[a]
                break
        #找到第二个拐点
        revers = y[::-1]
        for i,curlel in enumerate(revers):
            if  i < len(y)-minindex:
                continue
            if curlel > MIN_RMS + 2*pre_std:
                break
        secondConvertime = (len(y)-i) * frame_shift / fs
        #计算后验噪声
        postdata = y[int(len(y)-i):]
        post_std = np.std(postdata, ddof=1)
        post_Degrad  = get_rms(datanew[int(secondConvertime*fs):])
        noise_src = MAX_RMS - nosieVariable[noiseType] / 2
        post_src = get_rms(datanew[:int(firstconvertime*fs)])
        # print('firstconvertime  is {}'.format(firstconvertime))
        # print('secondConvertime  is {}'.format(secondConvertime))
        # print('prestd  is {}'.format(pre_std))
        # print('poststd  is {}'.format(post_std))
        # print('noise src is {}'.format(noise_src))
        # print('post noise src is {}'.format(post_src))
        # print('noise floor is {}'.format(Floor))
        # print('noise Degrad is {}'.format(Degrad))
        # print('post noise Degrad is {}'.format(post_Degrad))
        # print('ns gain is {}'.format(post_src-post_Degrad))


        # import matplotlib.pyplot as plt
        # plt.plot(x,y)
        # plt.show()
        return firstconvertime,secondConvertime,Floor,post_src,post_Degrad,post_std
    else:
        result = get_data_pairs(srcFile=srcFile, testFile=testFile)
        if result is not None:
            srcdata, dstdata, fs, chn = result
            return  cal_noise_converge(srcdata,dstdata,fs,chn)
        else:
            return result


if __name__ == '__main__':
    # src = '04_car_noise_speech.wav'
    # dst1= 'res_2023-09-12-15-00-33.wav'
    # dst = 'speech_cn.wav'
    # dst2 = 'mixDstFile3.wav'
    # dur = cal_noise_Supp(src,dst1)
    # print(dur)
    # speech_cn = r'D:\MARTIN\audiotestalgorithm-master\algorithmLib\Noise_Suppression\归档\nertc_music_iphone11_test____\anr\Speech\01_Common_clean_files\speech_cn\nertc\0\speech_cn.wav'
    # testfile = r'D:\MARTIN\audiotestalgorithm-master\algorithmLib\Noise_Suppression\归档\nertc_music_iphone11_test____\anr\Speech\agoraTestCase_63_beat_10\agora_speech_cn\0\mixDstFile.wav'
    # mixfile = r'D:\MARTIN\audiotestalgorithm-master\algorithmLib\Noise_Suppression\归档\nertc_music_iphone11_test____\anr\Speech\agoraTestCase_63_beat_10\agora_speech_cn\0\mixFile.wav'
    # delay = cal_fine_delay_of_specific_section(reffile=speech_cn,testfile=testfile,outfile='out.wav')
    # print(delay)
    # #dur = cal_noise_Supp_by_ref(srcFile=mixfile,testFile='out.wav',speechSection=[[17.32, 28.856]],musicMode=True)
    # dur = cal_transient_noise_Supp_by_ref(srcFile=mixfile, testFile='out.wav',
    #                             speechSection=[[16.43,18.78],[19.57,21.365],[22.01,24.22]],musicMode=False,noisetype='beat')
    #print(dur)

    import twine

    filepath = r'D:/MARTIN/归档/'
    blankfile = r'D:/MARTIN/blank.wav'
    from commFunction import get_file_path
    noiseList = []
    get_file_path(filepath,noiseList,[])
    print(noiseList)
    blankData,fs,ch = get_data_array(blankfile)
    for subfile in noiseList:
        curdata,fs,ch=get_data_array(subfile)
        curbase = os.path.basename(subfile)[:-4]
        overallarray = np.array([])

        fileLen = 27*fs
        noise,pause = len(curdata),len(curdata)*2
        print(noise)
        print(subfile)
        #continue
        n = int(fileLen // (noise + pause))
        curblankdata = blankData[:pause]
        for i in range(n):
            overallarray = np.concatenate((overallarray,curdata))
            overallarray = np.concatenate((overallarray, curblankdata))
        extraArray = np.concatenate((curdata,curblankdata))
        extra = fileLen - (noise + pause) * n
        overallarray = np.concatenate((overallarray, extraArray[:extra]))


        outfile =  "noise4speech/" + curbase + '_-20_20s.wav'
        make_out_file(outfile,overallarray,fs,ch)

        factor = 10 ** (-5 / 20)
        overallarray = overallarray * factor
        outfile =  "noise4speech/" + curbase + '_-25_20s.wav'
        make_out_file(outfile,overallarray,fs,ch)

        overallarray = overallarray * factor
        outfile =  "noise4speech/" + curbase + '_-30_20s.wav'
        make_out_file(outfile,overallarray,fs,ch)

        overallarray = np.array([])
        fileLen = 33*fs
        noise,pause = len(curdata),len(curdata)*2
        n = int(fileLen // (noise + pause))
        curblankdata = blankData[:pause]
        for i in range(n):
            overallarray = np.concatenate((overallarray,curdata))
            overallarray = np.concatenate((overallarray, curblankdata))
        extraArray = np.concatenate((curdata,curblankdata))
        extra = fileLen - (noise + pause) * n
        overallarray = np.concatenate((overallarray, extraArray[:extra]))


        outfile =  'noise4music/'  +curbase + '_-20_20s.wav'
        make_out_file(outfile,overallarray,fs,ch)

        factor = 10 ** (-5 / 20)
        overallarray = overallarray * factor
        outfile = "noise4music/" + curbase + '_-25_20s.wav'
        make_out_file(outfile, overallarray, fs, ch)

        overallarray = overallarray * factor
        outfile = "noise4music/" + curbase + '_-30_20s.wav'
        make_out_file(outfile, overallarray, fs, ch)



    pass