
import sys
import  os
import time
from os import  path
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
from formatConvert.wav_pcm import wav2pcm,pcm2wav
from PESQ.PESQ import cal_pesq
from POLQA.polqa_client import  polqa_client_test
from STI.cal_sti import cal_sti
from PEAQ.PEAQ import cal_peaq
from resample.resampler import resample,restruct
from timeAligment.time_align import cal_fine_delay,cal_fine_delay_of_specific_section
import os
import wave
import numpy as np
from ctypes import  *
from SNR_ESTIMATION.MATCH_SIG import match_sig
from SNR_ESTIMATION.SNR_MUSIC import cal_snr_music
from AGC_EVALUATION.CAL_MUSIC_STABILITY import cal_music_stablility
from FUNCTION.audioFunction import isSlience,audioFormat,get_rms_level,get_effective_spectral,cal_pitch,cal_EQ
from CLIPPING_DETECTION.audio_clip_detection import cal_clip_index
from commFunction import make_out_file,get_data_array

allMetrics = ['ALL','POLQA','PEAQ','LOUDNESS','MUSIC','MATCH','MUSICSTA','SLIENCE','FORMAT','TOTALRMS','AVERMS','PEAKRMS','STDRMS','MAXRMS','MINRMS','DYNMIC','LRATE','CLIP','DELAY','SPEC','PITCH','EQ','MATCH2','MATCH3']


class computeAudioQuality():
    def __init__(self,**kwargs):
        """
        :param kwargs:
        """
        #print(**kwargs)
        self.__parse_para(**kwargs)
        self.__chcek_valid()
        pass

    def __parse_para(self,**kwargs):
        """
        :param kwargs:
        :return:
        """
        self.mertic = kwargs['metrics']
        self.testFile = kwargs['testFile']
        self.refFile = kwargs['refFile']
        self.outFile = kwargs['outFile']
        self.audioType = kwargs["audioType"]
        self.rmsCalsection = kwargs["rmsCalsection"]
        self.polqaMode = kwargs["polqaMode"]
        self.pitchLogMode = kwargs["pitchLogMode"]
        self.fineDelaySection = kwargs["fineDelaySection"]
        self.rmsSpeechOnly = kwargs["rmsSpeechOnly"]

        self.testFile_L,self.testFile_R = self.Extract_Mono(self.testFile)

        self.refFile_L, self.refFile_R = self.Extract_Mono(self.refFile)
        if self.outFile is not None:
            self.outFile_L, self.outFile_R = self.outFile[:-4] + '_L.wav',self.outFile[:-4] + '_R.wav'
        if self.refFile is not None:
            self.__double_end_check()
    def Extract_Mono(self,audioFile):
        """
        :return:
        """
        try:
            stereo_data,frame,nchanel = get_data_array(audioFile)
            left_data = stereo_data[::2]
            right_data = stereo_data[1::2]
            l_name,r_name = audioFile[:-4] + '_L.wav',audioFile[:-4] + '_R.wav'
            make_out_file(l_name, left_data, frame, 1)
            make_out_file(r_name, right_data, frame, 1)
            return  l_name,r_name
        except:
            return None,None



    def __chcek_valid(self):
        """
        :return:
        """
        if self.mertic not in allMetrics:
            raise ValueError('matrix must betwin ' + str(allMetrics))

    def __check_format(self,curWav):
        """
        :param curWav:
        :return:
        """
        curType = os.path.splitext(curWav)[-1]
        if curType !='.wav':
            raise TypeError('audio format must be wav ')
        wavf = wave.open(curWav,'rb')
        curChannel = wavf.getnchannels()
        cursamWidth = wavf.getsampwidth()
        cursamplerate = wavf.getframerate()
        wavf.close()
        if curChannel != 2:
            raise ValueError('wrong type of channel' + curWav)
        if cursamWidth != 2:
            raise ValueError('wrong type of samWidth' + curWav)
        if cursamplerate != 48000:
            raise ValueError('wrong type of samplerate' + curWav)
        return curChannel,cursamWidth,cursamplerate

    def __double_end_check(self):
        """
        :return:
        """
        if  self.refFile is None or self.testFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.testFile) != self.__check_format(self.refFile):
            raise TypeError('there are different parametre in inputfiles!')


    def POLQA(self):
        """
        #POLQA  窄带模式  8k   超宽带模式 48k
        # pcm输入
        :return:
        """

        curCH,curBwidth,curSR = self.__check_format(self.testFile)
        result_l =  polqa_client_test(wav2pcm(self.refFile_L),wav2pcm(self.testFile_L),curSR,mode=self.polqaMode)
        result_r = polqa_client_test(wav2pcm(self.refFile_R), wav2pcm(self.testFile_R), curSR, mode=self.polqaMode)
        time.sleep(2)
        return  result_l,result_r


    def PEAQ(self):
        """
        # wav输入
        :return:
        """
        #TODO 计算peaq
        return cal_peaq(self.refFile_L,self.testFile_L),cal_peaq(self.refFile_R,self.testFile_R)
        pass



    def MUSIC(self):
        """
        # MUSIC SNR
        # 无采样率限制
        # WAV/PCM 输入
        :return:
        """
        return cal_snr_music(refFile=self.refFile_L,testFile=self.testFile_L),cal_snr_music(refFile=self.refFile_R,testFile=self.testFile_R)


    def MATCH(self):
        """
        # MATCH SIG
        # 无采样率限制
        # 可选择是否输出文件
        # WAV/PCM 输入
        :return:
        """
        left = match_sig(self.refFile_L, self.testFile_L, self.outFile_L,self.audioType)
        right = match_sig(self.refFile_R, self.testFile_R, self.outFile_R,self.audioType)
        return left,right


    def MATCH2(self):
        """
        """
        left = cal_fine_delay(self.refFile_L, self.testFile_L, outfile=self.outFile_L)
        right = cal_fine_delay(self.refFile_R, self.testFile_R, outfile=self.outFile_R)
        return left, right


    def MATCH3(self):
        """
        """
        left = cal_fine_delay_of_specific_section(self.refFile_L, self.testFile_L, outfile=self.outFile_L,speech_section=self.fineDelaySection)
        right = cal_fine_delay_of_specific_section(self.refFile_R, self.testFile_R, outfile=self.outFile_R,speech_section=self.fineDelaySection)
        return left, right


    def LOUDNESS(self):
        """
        Returns
        -------

        """
        pass


    def MUSICSTA(self):
        """
        AGC PARA 3
        计算music 信号稳定性
        :return:
        """
        return cal_music_stablility(refFile=self.refFile_L,testFile=self.testFile_L),cal_music_stablility(refFile=self.refFile_R,testFile=self.testFile_R)



    def SLIENCE(self):
        """
        Returns
        -------

        """
        return isSlience(self.testFile_L,section=self.rmsCalsection),isSlience(self.testFile_R,section=self.rmsCalsection)

    def FORMAT(self):
        """
        Returns
        -------

        """
        return audioFormat(self.testFile)


    def TOTALRMS(self):
        """
        Returns
        -------
        # (wavFileName=None,rmsMode='total',startTime=0,endTime=1):
        """


        return get_rms_level(wavFileName=self.testFile_L, rmsMode='total', section=self.rmsCalsection,
                             speechOnly=self.rmsSpeechOnly), get_rms_level(wavFileName=self.testFile_R, rmsMode='total',
                                                                           section=self.rmsCalsection,
                                                                           speechOnly=self.rmsSpeechOnly)

    def PEAKRMS(self):
        """
        Returns
        -------
        # (wavFileName=None,rmsMode='total',startTime=0,endTime=1):
        """
        return get_rms_level(wavFileName=self.testFile_L,rmsMode='peak',section=self.rmsCalsection,speechOnly=self.rmsSpeechOnly),get_rms_level(wavFileName=self.testFile_R,rmsMode='peak',section=self.rmsCalsection,speechOnly=self.rmsSpeechOnly)

    def STDRMS(self):
        """
        Returns
        -------
        # (wavFileName=None,rmsMode='total',startTime=0,endTime=1):
        """
        return get_rms_level(wavFileName=self.testFile_L,rmsMode='std',section=self.rmsCalsection,speechOnly=self.rmsSpeechOnly),get_rms_level(wavFileName=self.testFile_R,rmsMode='std',section=self.rmsCalsection,speechOnly=self.rmsSpeechOnly)


    def AVERMS(self):
        """
        Returns
        -------

        """
        return get_rms_level(wavFileName=self.testFile_L,rmsMode='average',section=self.rmsCalsection,speechOnly=self.rmsSpeechOnly),get_rms_level(wavFileName=self.testFile_R,rmsMode='average',section=self.rmsCalsection,speechOnly=self.rmsSpeechOnly)

    def MAXRMS(self):
        """
        Returns
        -------

        """
        return get_rms_level(wavFileName=self.testFile_L, rmsMode='max', section=self.rmsCalsection,
                             speechOnly=self.rmsSpeechOnly), get_rms_level(wavFileName=self.testFile_R,
                                                                           rmsMode='max',
                                                                           section=self.rmsCalsection,
                                                                           speechOnly=self.rmsSpeechOnly)

    def MINRMS(self):
        """
        Returns
        -------

        """
        return get_rms_level(wavFileName=self.testFile_L, rmsMode='min', section=self.rmsCalsection,
                             speechOnly=self.rmsSpeechOnly), get_rms_level(wavFileName=self.testFile_R,
                                                                           rmsMode='min',
                                                                           section=self.rmsCalsection,
                                                                           speechOnly=self.rmsSpeechOnly)
    def DYNMIC(self):
        """
        Returns
        -------

        """
        return get_rms_level(wavFileName=self.testFile_L, rmsMode='dynmic', section=self.rmsCalsection,
                             speechOnly=self.rmsSpeechOnly), get_rms_level(wavFileName=self.testFile_R,
                                                                           rmsMode='dynmic',
                                                                           section=self.rmsCalsection,
                                                                           speechOnly=self.rmsSpeechOnly)



    def CLIP(self):
        """
        Returns
        -------

        """
        return cal_clip_index(self.testFile_L),cal_clip_index(self.testFile_R)



    def SPEC(self):
        """
        Returns
        -------

        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        return get_effective_spectral(self.testFile_L),get_effective_spectral(self.testFile_R)


    def PITCH(self):
        """
        Returns
        -------

        """
        self.__double_end_check()
        return cal_pitch(self.refFile_L, self.testFile_L,pitchlogMode=self.pitchLogMode),cal_pitch(self.refFile_R, self.testFile_R,pitchlogMode=self.pitchLogMode)


    def EQ(self):
        """
        Returns
        -------

        """
        self.__double_end_check()
        return cal_EQ(self.refFile_L,self.testFile_L),cal_EQ(self.refFile_R,self.testFile_R)


    def FR(self):
        pass

    def PLAY_DELAY(self):
        pass

    def VISQOL(self):
        pass

    def L_R_Cons(self):
        pass

    def ALL(self):

        pass