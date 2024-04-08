# -*- coding:utf-8 -*-
import copy
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
sys.path.append(path.dirname(__file__))
from commFunction import getip,log_time,global_result,sftp_connect,sftp_put,sftp_disconnect,get_rms
import shutil
from  socketClient import SocketClient
import numpy as np

cur_server_name = 'serverB'
cur_server_name_2 = 'serverC'
request_method = 'request'
response_method = 'response'


# def polqa_client_auto(src,test,samplerate,mode=0):
#
#

# TODO ????,????

def polqa_client_test(src,test,samplerate,mode=0):
    reslut = sigal_test(src,test,samplerate,mode=mode)
    if reslut ['err'] == 'POLQA Software Error!' or reslut ['err']  == 'Time out':
        cur_server = reslut['server']
        if cur_server == cur_server_name:
            reslut = sigal_test(src, test, samplerate, mode=mode,server=cur_server_name_2)
            return reslut['result']
        if cur_server == cur_server_name_2:
            reslut = sigal_test(src, test, samplerate, mode=mode,server=cur_server_name)
            return reslut['result']
    return reslut['result']



def sigal_test(src,test,samplerate,mode=0,server='random'):

    curip = getip()
    curtime = log_time()
    curpath = str(curip) + '_'+str(curtime)
    os.mkdir(curpath)

    if mode == 1:
        f = open(test, "rb")
        curaudiodata = np.fromfile(f, dtype=np.int16)
        curaudiodata = curaudiodata.astype(np.float64)
        currms = get_rms(curaudiodata)
        adjustlevel = -26 - currms

        factor = 10 ** (adjustlevel / 20)
        urframe = curaudiodata * factor
        urframe = urframe.astype(np.int16)
        urframe.tofile(test)
        f.close()
    curdata = global_result.get_data()
    curdata['module'] = 'clientA'
    curdata['method'] = 'requestA'
    curdata['samplerate'] = samplerate
    curdata['token'] = curpath
    curdata['srcFile'] = os.path.basename(src)
    curdata['testFile'] = os.path.basename(test)
    curdata['server'] = server
    curdata['timeOut'] = 25

    #ssh
    shutil.copy(src,curpath)
    shutil.copy(test, curpath)

    dstpath = '/home/netease/polqa'


    # stfp
    client,sftp = sftp_connect(global_result.username,global_result.password,global_result.HOST,port=global_result.sftpPort)
    sftp_put(sftp,curpath, dstpath)
    sftp_disconnect(client)

    shutil.rmtree(curpath,ignore_errors=True)
    # get result
    socket = SocketClient(global_result.machost,global_result.PORT)
    try:
        result = socket.sender(curdata)
        print(result)
    except:
        socket.close()
        return None
    return  result


if __name__ == '__main__':
    import platform
    print(platform.uname())
    print(sys.platform)

    # polqa_client_test(src='src.pcm',test='test.pcm',samplerate=48000,mode=0)
    #
    # exit(0)
    # client, sftp = sftp_connect(username, password, serverIP, port=port)
    # sftp_get(sftp, '/home/netease/polqa_result/' + '192.168.1.3_2021-08-18-17-52-35' + '.ress', 'result')
    src = r'speech_QualityTest_ref.pcm'
    test1 = r'0sub_7_idealy.pcm'
    test2 = r'D:\0\mixDstFile_minus_13_-6.pcm'
    refout = r'E:\AIVAD\OTHER\ref_out0_01.pcm'
    file = r'E:\AIVAD\OTHER\reverse0_01.pcm'
    info = polqa_client_test(src, src, 48000)
    print(info)
    exit(0)
    path = r'E:\02_POLQA_RESULT\testDstFiles\NERTC_iphone11_honor8x_V4.3.0\L\Speech_48000\NONE\female\femalePOLQASWB'
    src = r'E:\01_MOS_AUTO_TESTER\testSrcFiles\Speech_48000\female\femalePOLQASWB.pcm'
    filelist = []
    f = open('time.txt','w')

    get_file_path(path,filelist,[])
    print(filelist)
    #print(exists_remote('10.219.33.45','/home/netease/polqa_result/455.ss'))
    for a in range (1000):
        for file in filelist:
            print('*****************************************************')
            print('curent testfile name is {0},srcfile name is {1}'.format(file,src))
            begin_time = datetime.datetime.now()
            info = polqa_client_test(src, file,48000)
            end_time = datetime.datetime.now()
            duration = end_time - begin_time
            print('time duration is {}'.format(duration))
            f.writelines('*****************************************************\n')
            f.writelines('file name is {}\n'.format(file))
            f.writelines('result is {}\n'.format(str(info)))
            f.writelines('time duration is {}\n'.format(duration))
    f.close()
    #vqtDisConnect
    # for a in range(100):
    #     polqa_client_test(srcfile,testfile)
