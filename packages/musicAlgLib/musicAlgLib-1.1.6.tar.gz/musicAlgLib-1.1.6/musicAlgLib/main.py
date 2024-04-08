from operator import methodcaller
from computeAudioQuality.mainProcess import computeAudioQuality
from ctypes import  *

def compute_music_quality(metrics,testFile=None,refFile=None,outFile=None,audioType=1,
                         rmsCalsection=None,polqaMode=0,pitchLogMode=1,fineDelaySection=None,rmsSpeechOnly=False,rmsFrameDuration=0.05,rmsShiftDuration=0.05):
    """
    :param metrics: ['ALL','POLQA','PEAQ','LOUDNESS','MUSIC','MATCH','MUSICSTA','SLIENCE','FORMAT','TOTALRMS','AVERMS','PEAKRMS','STDRMS','MAXRMS','MINRMS','DYNMIC','LRATE','CLIP','DELAY','SPEC','PITCH','EQ','MATCH2','MATCH3']

    #
    # POLQA 窄带模式  8k  超宽带模式 48k ；WAV/PCM输入 ；双端输入：ref、test；时长 < 20s；
    # PEAQ 无采样率限制；WAV/PCM输入 ；双端输入：ref、test；无时间长度要求；
    # MATCH 无采样率限制; WAV/PCM输入;三端输入：ref、test、out； 无时间长度要求；
    # MUSIC 无采样率限制;WAV/PCM输入;双端输入：ref、test；无时间长度要求；
    # MUSICSTA 无采样率限制,WAV/PCM输入;双端输入：ref、test；无时间长度要求；
    # SLIENCE 无采样率限制 WAV/PCM/MP4输入;单端输入：test；无时间长度要求；
    # FORMAT 无采样率限制 WAV/MP4输入;单端输入：test；无时间长度要求；
    # TRMS 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # ARMS 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # PRMS 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # NOISE 无采样率限制 WAV/PCM输入 ；双端输入：ref、test；无时间长度要求；
    # CLIP 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # DELAY 无采样率限制; WAV/PCM输入;双端输入：ref、test； 无时间长度要求；
    # SPEC 无采样率限制; WAV/PCM输入;单端输入：test； 无时间长度要求；
    # PITCH 无采样率限制；WAV/PCM输入;双端输入：ref、test； 无时间长度要求；
    # EQ 无采样率限制；WAV/PCM输入;双端输入：ref、test； 无时间长度要求；
    # MATCH2 无采样率限制; WAV/PCM输入;三端输入：ref、test、out； 无时间长度要求；
    # MATCH3 无采样率限制; WAV/PCM输入;三端输入：ref、test、out； 无时间长度要求；
    不同指标输入有不同的采样率要求，如果传入的文件不符合该指标的要求，会自动变采样到合法的区间
    :param testFile: 被测文件，必选项
    :param refFile:  参考文件，可选项，全参考指标必选，比如POLQA/PESQ/PEAQ
    :param outFile 输出文件，可选项，对齐文件可选
    :param audioType  输入音频的模式 0：语音 1：音乐 MATCH/GAINTABLE需要
    :param rmsCalsection 计算rms的区间 TRMS和ARMS需要，时间单位s，比如：[1,20]
    :param polqaMode 计算polqa的模式 0:默认模式  1: 理想模式：排除小声音的影响，把声音校准到理想点平 -26db
    :param pitchLogMode 计算pitch的模式 0：线性模式，用于SetLocalVoicePitch接口; 1：对数模式,用于SetAudioMixingPitch接口；默认为1
    :param fineDelaySection 精准计算延时(MTACH3)，需要手动标出语音块的位置，比如有三段：speech_section=[[2.423,4.846],[5.577,7.411],[8,10.303]]
    :param rmsFrameDuration 计算rms的帧长度 默认50ms
    :param rmsShiftDuration 计算rms的帧移 默认50ms
    :return:
    """
    paraDicts = {
        'metrics':metrics,
        'testFile':testFile,
        'refFile':refFile,
        'outFile':outFile,
        "audioType":audioType,
        'rmsCalsection':rmsCalsection,
        'polqaMode':polqaMode,
        "pitchLogMode":pitchLogMode,
        "fineDelaySection":fineDelaySection,
        "rmsSpeechOnly":rmsSpeechOnly,
        'rmsFrameDuration' : rmsFrameDuration,
        'rmsShiftDuration' : rmsShiftDuration
    }
    comAuQUA = computeAudioQuality(**paraDicts)
    return methodcaller(metrics)(comAuQUA)

if __name__ == '__main__':

    # speech = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\speech.wav'
    # music = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\music_rap.wav'
    # transi = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\transientNoise.wav'
    # test = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\test.wav'
    # res = compute_audio_quality('MUSIC',refFile=speech,testFile=music)
    #
    # print(res)
    #
    # res = compute_audio_quality('TRANSIENT',cleFile=speech,noiseFile=transi,testFile=test)
    # print(res)
    #
    # res = compute_audio_quality('MATCH',refFile=speech,testFile=test,outFile='123.wav')
    # print(res)
    #print(compute_audio_quality('G160', testFile=src,refFile=src,samplerate=16000))

    #print(match_sig(refFile='speech.wav', targetFile='test.wav', outFile='outfile.wav'))
    import time
    for a in range(200):
        time.sleep(1)
        src = r'E:\audioalgorithm\audiotestalgorithm\demos\02_p563_demo\cleDstFile.wav'
        print(compute_audio_quality('P563',testFile=src))
    exit(0)
    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_attackrelease.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test_attackrelease.wav'
    print(compute_audio_quality('ATTACKRELEASE',refFile=file,testFile=test))

    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test.wav'
    lim,gain_table,DR = compute_audio_quality('GAINTABLE',refFile=file,testFile=test,audioType=1)
    print(lim,gain_table[0],DR[2])
    for a in gain_table:
        print(a)
    for a in DR:
        print(a)

    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\music_stability_.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test_music_stability.wav'
    res = compute_audio_quality('MUSICSTA',refFile=file, testFile=test)
    for a in res:
        print(a)

    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test.wav'
    delay = compute_audio_quality('AGCDELAY',refFile=file,testFile=test)
    print(delay)

    compute_audio_quality('MATCH',refFile=file,testFile=test,outFile='out.wav',audioType=1)