import wave
import sys,os
from os import  path
sys.path.append(path.dirname(__file__))
sys.path.append(os.path.dirname(path.dirname(__file__)))
from moviepy.editor import AudioFileClip
from commFunction import get_rms,get_ave_rms,get_one_channel_data,get_file_duration,get_data_array,get_peak_rms,get_std_rms,get_duration_above_specific_rms,get_max_rms,get_min_rms
from formatConvert import pcm2wav
import numpy as np
import scipy.signal as signal
import math
import librosa
from PCC.Pearson_CC import get_max_cc_by_dll
import ctypes,os,platform
from ctypes import *
from timeAligment.time_align import cal_fine_delay_of_specific_section
from VAD_NN.hubconf import silero_vad

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
def get_wav_from_mp4(mp4file):
    """
    Parameters
    ----------
    mp4file

    Returns
    -------

    """
    suffix = os.path.splitext(mp4file)[-1]
    if suffix != '.mp4':
        raise TypeError('wrong format! not mp4 file!' + str(suffix))
    my_audio_clip = AudioFileClip(mp4file)
    newFileName = mp4file[:-4] + '.wav'
    my_audio_clip.write_audiofile(newFileName)
    return newFileName


def isSlience(Filename =None,section=None,channels=2, bits=16, sample_rate=48000):
    """
    Parameters
    ----------
    Filename 支持 wav 和 pcm 和MP4

    Returns
    -------

    """
    suffix = os.path.splitext(Filename)[-1]

    if suffix == '.mp4':
        Filename = get_wav_from_mp4(Filename)
    if suffix == '.pcm':
        Filename = pcm2wav(Filename,channels,bits,sample_rate)
    if suffix == '.wav':
        pass
    lenth,fs = get_file_duration(Filename)
    data = get_one_channel_data(Filename)
    if section is None:
        startTime = 0
        endTime = lenth
    else:
        startTime = section[0]
        endTime = section[1]
    if startTime > lenth or startTime > endTime:
        raise TypeError('start point is larger than the file lenth :' + str(suffix))
    if endTime > lenth:
        endTime = lenth
    ins = data[int(startTime*fs):int(endTime*fs)]

    dBrmsValue = get_rms(ins)#20*math.log10(get_rms(ins)/32767+ 1.0E-6)
    print(dBrmsValue)
    if dBrmsValue > -70:
        return False
    else:
        for n in range(len(ins)//480):
            curdata = ins[480*n:480*(n+1)]
            dBrmsValue = get_rms(curdata)#20 * math.log10(get_rms(curdata) / 32767 + 1.0E-6)
            print(dBrmsValue)
            if dBrmsValue > -60:
                return False
        return True
    pass


def audioFormat(wavFileName=None):
    """
    wavFileName：输入文件 wav，mp4
    Returns
    -------
    refChannel:通道数
    refsamWidth：比特位 2代表16bit
    refsamplerate：采样率
    refframeCount：样点数
    """
    suffix = os.path.splitext(wavFileName)[-1]
    if suffix != '.wav' and suffix != '.mp4':
        raise TypeError('wrong format! not wav/mp4 file!' + str(suffix))
    if suffix == '.mp4':
        wavFileName = get_wav_from_mp4(wavFileName)
    wavf = wave.open(wavFileName, 'rb')
    refChannel,refsamWidth,refsamplerate,refframeCount = wavf.getnchannels(),wavf.getsampwidth(),wavf.getframerate(),wavf.getnframes()
    return refChannel,refsamWidth*8,refsamplerate,refframeCount

def get_rms_level(wavFileName=None,rmsMode='total',section=None,speechOnly=False,frameDuration=0.05,shiftduration=0.05):
    """
    wavFileName：输入文件 wav，mp4
    Returns
    -------
    refChannel:通道数
    refsamWidth：比特位 2代表16bit
    refsamplerate：采样率
    refframeCount：样点数
    """
    suffix = os.path.splitext(wavFileName)[-1]
    if suffix != '.wav':
        raise TypeError('wrong format! not wav file!' + str(suffix))

    lenth,fs = get_file_duration(wavFileName)
    data = get_one_channel_data(wavFileName)
    if section == None:
        startTime = 0
        endTime = lenth
    else:
        startTime = section[0]
        endTime = section[1]
    if startTime > lenth or startTime > endTime:
        raise TypeError('start point is larger than the file lenth :' + str(suffix))
    if endTime > lenth:
        endTime = lenth
    curdata = data[int(startTime*fs):int(endTime*fs)]
    if section == None and speechOnly:
        speechSection = silero_vad(wavFileName)
        # TODO 选取最小的地方计算有效频谱
        testdata, fs, ch = get_data_array(wavFileName)
        curdata = np.array([])
        for eachSection in speechSection:
            curdata = np.concatenate(
                (curdata, testdata[int(fs * eachSection[0]):int(fs * eachSection[1])]))

    if rmsMode == 'total':
        return get_rms(curdata)
    if rmsMode == 'average':
        return get_ave_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration)
    if rmsMode == 'peak':
        return  get_peak_rms(curdata)
    if rmsMode == 'std':
        return  get_std_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration)
    if rmsMode == 'max':
        return  get_max_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration)
    if rmsMode == 'min':
        return  get_min_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration)
    if rmsMode == 'dynmic':
        return  get_max_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration) - get_min_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration)
    if rmsMode == 'duration':
        return  get_duration_above_specific_rms(curdata,fs,frameDuration=frameDuration,shiftduration=shiftduration)
    return None



def calculate_band_energy(audio_signal, sample_rate, num_bands,freq_mode='upper'):
    # Perform FFT on audio signal
    fmin,fmax = 100,sample_rate/2 - 100
    freq_points = np.linspace(0, sample_rate/2, num_bands+1)
    #freq_points = np.logspace(0, sample_rate / 2, num_bands + 1)
    # Compute center frequencies of each band
    center_freqs = freq_points[:-1] + np.diff(freq_points)/2
    # Compute bandwidth of each band
    bandwidths = np.diff(freq_points)

    # Compute lower and upper frequency limits of each band
    lower_freqs = center_freqs - bandwidths/2
    upper_freqs = center_freqs + bandwidths/2

    # Clip lower and upper frequency limits to specified range
    lower_freqs = np.clip(lower_freqs, fmin, fmax)
    upper_freqs = np.clip(upper_freqs, fmin, fmax)
    # Define bandpass filter for each frequency band
    b, a = signal.butter(4, [lower_freqs[0], upper_freqs[-1]], 'bandpass', fs=sample_rate)
    band_filters = [signal.butter(4, [lower_freqs[i], upper_freqs[i]], 'bandpass', fs=sample_rate) for i in range(num_bands)]

    # Apply each bandpass filter to the FFT signal
    band_signals = [signal.filtfilt(band_filters[i][0], band_filters[i][1], audio_signal.astype(np.float32)) for i in range(num_bands)]


    # Calculate energy for each frequency band
    band_energy = [ get_rms(band_signals[i]) for i in range(num_bands)]


    if freq_mode == 'upper':
        return band_energy,upper_freqs
    if freq_mode == 'lower':
        return band_energy,lower_freqs
    if freq_mode == 'centre':
        return band_energy,center_freqs

def calculate_octave_band_energy(audio_signal,sample_rate):
    # Perform FFT on audio signal
    # Calculate the number of bands

    num_bands = 10
    center_freqs = [31,62,125,250,500,1000,2000,4000,8000,16000]
    sample_rate_list = [100,200,400,1000,1600,3000,6000,12000,24000,48000]
    # Print the band limits
    lower_freqs = []
    upper_freqs = []
    for i in range(len(center_freqs)):
        upper_freqs.append(center_freqs[i]*2**(0.5))
        lower_freqs.append(center_freqs[i]/(2**(0.5)))

    # Define bandpass filter for each frequency band
    #b, a = signal.butter(4, [lower_freqs[0], upper_freqs[0]], 'bandpass', fs=8000)
    band_filters = [signal.butter(4, [lower_freqs[i], upper_freqs[i]], 'bandpass', fs=sample_rate_list[i]) for i in range(num_bands)]
    #print(band_filters)
    # Apply each bandpass filter to the FFT signal
    band_signals = [signal.filtfilt(band_filters[i][0], band_filters[i][1],  librosa.resample(audio_signal.astype(np.float32),orig_sr=sample_rate,target_sr=sample_rate_list[i]) ) for i in range(num_bands)]


    # Calculate energy for each frequency band
    band_energy = [ get_rms(band_signals[i]) for i in range(num_bands)]
    return band_energy, center_freqs

def find_index(lst):
    last_elem = lst[-1]
    for i, elem in reversed(list(enumerate(lst))):
        if elem - last_elem > 9:
            return i
    return -1





def get_effective_spectral(audiofile):

    speechSection = silero_vad(audiofile)

    #TODO 选取最小的地方计算有效频谱
    testdata,fs,ch = get_data_array(audiofile)


    testallarray = np.array([])
    for eachSection in speechSection:
        testallarray= np.concatenate((testallarray,testdata[int(fs*eachSection[0]):int(fs*eachSection[1])]))

    #audio_data, sample_rate, ch = get_data_array(audiofile)
    FRAME_LEN = 960
    frame_shift = 480

    n_sengen = (len(testallarray) - FRAME_LEN) // frame_shift
    max_level,min_level = -99,99
    for a in range(n_sengen):
        cursrcLevel = get_rms(testallarray[a * frame_shift:a * frame_shift + FRAME_LEN])
        if cursrcLevel >max_level:
            max_level = cursrcLevel
        if cursrcLevel < min_level:
            min_level = cursrcLevel
    print(max_level,min_level,'++++')
    thirdduration = (max_level-min_level) / 3
    max_level = min_level + thirdduration
    min_level = min_level - thirdduration
    # Calculate energy for each frequency
    sumlist = []
    for a in range(n_sengen):
        curdata = testallarray[a * frame_shift:a * frame_shift + FRAME_LEN]
        cursrcLevel = get_rms(curdata)
        if cursrcLevel > min_level and cursrcLevel < max_level:

        #if cursrcLevel
            test_energy, upper_freqs = calculate_band_energy(curdata, fs, 40)
            # for i in range(len(test_energy)):
            #     print(upper_freqs[i],test_energy[i])
            final_index = find_index(test_energy)
            #print(cursrcLevel,upper_freqs[final_index])
            sumlist.append(upper_freqs[final_index])

    print(sum(sumlist)/len(sumlist))
    return sum(sumlist)/len(sumlist)
    #print(min(sumlist))
    # Print energy values for each band
    #return upper_freqs[final_index]

def find_max_energy_frequency(file_path):
    # 加载声音文件
    data,rate,ch = get_data_array(file_path)
    # 去均值，去掉直流分量
    data = data - np.mean(data)
    # 计算FFT（快速傅里叶变换）
    n = len(data)
    if n % 2 == 1:
        data = np.append(data, 0)
        n += 1
    X = np.fft.rfft(data)
    X = X[:n//2+1]
    # 计算频域能量
    energy = np.abs(X)**2
    # 找到能量最大的频率
    f = np.linspace(0, rate / 2, len(X))
    max_energy_index = np.argmax(energy)
    max_energy_frequency = f[max_energy_index]

    return max_energy_frequency

def cal_pitch(ref_path,file_path,pitchlogMode=1):
    src_fs = find_max_energy_frequency(ref_path)
    ds_fs = find_max_energy_frequency(file_path)
    assert pitchlogMode == 0 or pitchlogMode == 1
    result = 0
    if pitchlogMode == 1:
        result = math.log(ds_fs/src_fs, 2) * 12
    if pitchlogMode == 0:
        result = ds_fs/src_fs
    return result

def get_subarray(arr, lower, upper):
    """
    在递增列表arr中，找到在[lower, upper]范围内的元素，返回新数组以及开始和结束位置的索引
    参数：
        arr: 一维递增的numpy数组
        lower: 范围的下限
        upper: 范围的上限
    返回值：
        一个元组，包含三个元素，第一个元素为新数组，第二个元素为开始位置的索引，第三个元素为结束位置的索引
    """
    # 将列表转换为一维numpy数组
    arr = np.array(arr)
    # 使用searchsorted函数寻找新数组的开始和结束位置
    start_index = np.searchsorted(arr, lower, side='left')
    end_index = np.searchsorted(arr, upper, side='right')
    # 使用切片语法提取新数组
    new_arr = arr[start_index:end_index]
    # 返回新数组以及开始和结束位置的索引
    return (new_arr, start_index, end_index - 1)

def find_max_min_diff_index(arr1, arr2, mode='max'):
    """
    Find the index of max or min absolute difference between two arrays

    :param arr1: first array
    :param arr2: second array
    :param mode: 'max' for maximum absolute difference, 'min' for minimum absolute difference
    :return: the index of the point with max or min absolute difference
    """
    arr1,arr2 = np.array(arr1),np.array(arr2)
    mask = np.isfinite(arr1) & np.isfinite(arr2)
    arr1 = arr1[mask]
    arr2 = arr2[mask]
    # 找到绝对值相差最大或最小的点
    if mode == 'max':
        diff = np.abs(arr1 - arr2)
        index = np.argmax(diff)
    elif mode == 'min':
        diff = np.abs(arr1 - arr2)
        index = np.argmin(diff)
    else:
        raise ValueError("Invalid mode, should be 'max' or 'min'")
    # 返回结果
    return (mask.nonzero()[0][index], diff[index])

def cal_EQ(ref_path,file_path):
    """
    """
    # ref_data,fs,ch = get_data_array('01_POLQA.wav')
    # ref_data = ref_data[int(fs*1.1):int(fs*2.7)]
    # print(ref_data)
    # ref_data_8k = librosa.resample(ref_data.astype(np.float32), orig_sr=fs ,target_sr=8000)


    refspec = get_effective_spectral(ref_path)
    testspec = get_effective_spectral(file_path)
    #print(refspec,testspec)
    maxfreq = min(refspec,testspec)
    minfreq = 100
    center_freqs = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    pre_data, sample_rate, ch = get_data_array(ref_path)

    # pre_data_8k = librosa.resample(pre_data.astype(np.float32), orig_sr=sample_rate, target_sr=8000)
    # maxCoin, startPoint = get_max_cc_by_dll(ref_data_8k, pre_data_8k, get_my_dll(), 3)
    # print(maxCoin,startPoint)
    # if maxCoin < 0.3:
    #     return None
    # pre_data = pre_data[int(startPoint):int(startPoint+sample_rate*1.5)]
    pre_energy, pre_freq = calculate_octave_band_energy(pre_data, sample_rate)


    #pre_energy, pre_freq = calculate_band_energy(pre_data, sample_rate,218)
    post_data, sample_rate, ch = get_data_array(file_path)
    # post_data_8k = librosa.resample(post_data.astype(np.float32), orig_sr=sample_rate, target_sr=8000)
    # maxCoin, startPoint = get_max_cc_by_dll(ref_data_8k, post_data_8k, get_my_dll(), 3)
    # print(maxCoin, startPoint)
    # if maxCoin < 0.3:
    #     return None
    # post_data = post_data[int(startPoint):int(startPoint+sample_rate*1.5)]
    post_energy, post_freq = calculate_octave_band_energy(post_data, sample_rate)
    #post_energy, post_freq = calculate_band_energy(post_data, sample_rate,218)
    newfreq,startindex,stopindex = get_subarray(pre_freq,minfreq,maxfreq)
    pre_energy = pre_energy[startindex:stopindex+1]
    post_energy = post_energy[startindex:stopindex+1]
    # for i in range(len(newfreq)):
    #     print(newfreq[i])
    #     print(pre_energy[i])
    #     print(post_energy[i])
    index,maxdiff = find_max_min_diff_index(pre_energy,post_energy)
    if maxdiff < 1:
        return None
    realdiff = 2*(post_energy[index]-pre_energy[index])
    result = 15 if realdiff > 15 else (-15 if realdiff < -15 else realdiff)
    return newfreq[index],result

def cal_stuck(filename):
    data,fs,ch = get_data_array(filename)
    FRAME_LEN = 480*2
    frame_shift = 480
    base_level = get_rms(data) - 9
    print(base_level)
    stuck_20_50_ms_cnt,stuck_20_50_ms_total = 0,0
    stuck_50_100_ms_cnt, stuck_50_100_ms_total = 0, 0
    stuck_100_200_ms_cnt, stuck_100_200_ms_total = 0, 0
    stuck_up_200_ms_cnt, stuck_up_200_ms_total = 0, 0
    stuck_all_ms_cnt,stuck_all_ms_total = 0,0
    n_sengen = (len(data) - FRAME_LEN) // frame_shift
    in_stuck_flag = False
    stuck_cnt = 0
    global_cnt = 0
    for a in range(n_sengen):
        global_cnt += 1
        if global_cnt < 50:
            continue
        cursrcLevel = get_rms(data[a * frame_shift:a * frame_shift + FRAME_LEN])
        if not in_stuck_flag  and cursrcLevel < base_level:
            in_stuck_flag = True
        if in_stuck_flag and cursrcLevel < base_level:
            stuck_cnt += 1
        if in_stuck_flag and cursrcLevel > base_level:
            in_stuck_flag = False
            if stuck_cnt <= 2:
                pass
            if 3 <= stuck_cnt <= 6:
                stuck_20_50_ms_cnt += 1
                curduration = (stuck_cnt) * frame_shift / fs
                stuck_20_50_ms_total += curduration
                stuck_all_ms_cnt += 1
                stuck_all_ms_total += curduration
                second = global_cnt*frame_shift/fs
                print(second//60,second%60,'30ms-50ms',curduration)
            if 6 < stuck_cnt <= 10:
                curduration = (stuck_cnt) * frame_shift / fs
                stuck_50_100_ms_cnt += 1
                stuck_50_100_ms_total += curduration
                stuck_all_ms_cnt += 1
                stuck_all_ms_total += curduration
                second = global_cnt * frame_shift / fs
                print(second // 60, second % 60, '50ms-100ms',curduration)
            if 10 < stuck_cnt <= 20:
                curduration = (stuck_cnt) * frame_shift / fs
                stuck_100_200_ms_cnt += 1
                stuck_100_200_ms_total += curduration
                stuck_all_ms_cnt += 1
                stuck_all_ms_total += curduration
                second = global_cnt * frame_shift / fs
                print(second // 60, second % 60, '100ms-200ms',curduration)
            if 20 < stuck_cnt:
                curduration = (stuck_cnt) * frame_shift / fs
                stuck_up_200_ms_cnt += 1
                stuck_up_200_ms_total += curduration
                stuck_all_ms_cnt += 1
                stuck_all_ms_total += curduration
                second = global_cnt * frame_shift / fs
                print(second // 60, second % 60, 'up200ms',curduration)
            stuck_cnt = 0
        #print(cursrcLevel)
    print(stuck_20_50_ms_cnt,stuck_20_50_ms_total)
    print(stuck_50_100_ms_cnt, stuck_50_100_ms_total)
    print(stuck_100_200_ms_cnt, stuck_100_200_ms_total)
    print(stuck_up_200_ms_cnt, stuck_up_200_ms_total)
    print(stuck_all_ms_cnt,stuck_all_ms_total)
if __name__ == '__main__':
    # file = 'res_2023-09-15-15-24-31.wav'
    # from commFunction import get_file_path
    # filelist = []
    # filepath = r'D:\MARTIN\audiotestalgorithm-master\algorithmLib\FUNCTION\testfile2'
    # get_file_path(filepath,filelist,[])
    # #filelist = [r'D:\MARTIN\audiotestalgorithm-master\algorithmLib\FUNCTION\testfile\agora_band.wav']
    # for file in filelist:
    #     print(file)
    #     cal_stuck(file)
    file = 'pre_process.wav'
    rms = get_rms_level(file,rmsMode='peak',speechOnly=True)
    print(rms)
    # freq_points = np.logspace(20, 20000,num=10)
    # print(freq_points)
    # freq,db = cal_EQ('pre_process.wav','post_process.wav')
    # print(freq,db)
    # ref = '8_final_speech.wav'
    # #print(isSlience(ref,section=[0,20]),)
    # #print(audioFormat(ref))
    #print(get_effective_spectral('pre_process_balnk.wav'))
    # @title Install and Import Dependencies

    # this assumes that you have a relevant version of PyTorch installed
    #get_effective_spectral('res.wav')

    # from VAD_NN.hubconf import silero_vad
    # print(silero_vad('01_POLQA.wav'))


