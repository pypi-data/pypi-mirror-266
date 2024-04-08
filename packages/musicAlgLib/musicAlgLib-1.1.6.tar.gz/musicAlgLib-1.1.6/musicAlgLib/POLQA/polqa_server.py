# -*- coding:utf-8 -*-

import  time

import copy
import sys,os
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
from commFunction import global_result,sftp_connect,sftp_get,sftp_disconnect,constMosResult
import shutil
from  socketClient import SocketClient
from POLQA import startvqt

cur_server_name = 'serverB'
cur_server_name_2 = 'serverC'
request_method = 'request'
response_method = 'response'



def exec_polqa_test():

    while(True):
        time.sleep(1)
        try:
            socket = SocketClient(global_result.machost,global_result.PORT)
            curdata = global_result.get_data()
            curdata['module'] = cur_server_name
            curdata['method'] = request_method
            curruslt = socket.sender(curdata)
        except:
            socket.close()
            continue
        if curruslt['job'] is None or str(curruslt['job']) == 'null':
            continue

        #try:
        print('processing')
        #检查文件
        print('revice data')
        print(curruslt)
        #链接sftp
        client,sftp = sftp_connect(global_result.username,global_result.password,global_result.HOST,port=global_result.sftpPort)
        sftp_get(sftp, '/home/netease/polqa/' + curruslt['token'], '')
        sftp_disconnect(client)
        srf ,tsf, fpath,sr = curruslt['token'] +'/'+ curruslt['srcFile'],curruslt['token'] +'/'+ curruslt['testFile'],curruslt['token'],curruslt['samplerate']
        global_result.mosResult = copy.deepcopy(constMosResult)

        if not os.path.exists(srf) or not os.path.exists(tsf):
            curruslt['err'] = 'lack of input files!'
            global_result.mosResult['err'] = 'lack of input files!'
            curruslt['result'] = global_result.mosResult
            curruslt['module'] = cur_server_name
            curruslt['method'] = response_method
            print('send data')
            print(curruslt)
            socket = SocketClient(global_result.machost, global_result.PORT)
            try:
                douresult = socket.sender(curruslt)
            except:
                socket.close()
            shutil.rmtree(fpath, ignore_errors=True)
            continue
        # TODO 判断 ‘-0.0’的case
        # TODO 判断PID进程
        # samplerate = info[3]
        startvqt(os.path.abspath(srf), os.path.abspath(tsf), sr)

        if 'No error' != global_result.mosResult['err']:
            curruslt['err'] = global_result.mosResult['err']
            curruslt['result'] = global_result.mosResult
            curruslt['module'] = cur_server_name
            curruslt['method'] = response_method
            print('send data')
            print(curruslt)
            socket = SocketClient(global_result.machost, global_result.PORT)
            try:
                douresult = socket.sender(curruslt)
            except:
                socket.close()
            shutil.rmtree(fpath, ignore_errors=True)
            continue
        if '-0.0' == global_result.mosResult['mos']:
            #time.sleep(5)
            curruslt['err'] = 'POLQA Software Error!'
            global_result.mosResult['err'] = 'POLQA Software Error!'
            curruslt['result'] = global_result.mosResult
            curruslt['module'] = cur_server_name
            curruslt['method'] = response_method
            print('send data')
            print(curruslt)
            socket = SocketClient(global_result.machost, global_result.PORT)
            try:
                douresult = socket.sender(curruslt)
            except:
                socket.close()
            shutil.rmtree(fpath, ignore_errors=True)
            continue
        curruslt['result'] = global_result.mosResult

        socket = SocketClient(global_result.machost, global_result.PORT)
        curruslt['module'] = cur_server_name
        curruslt['method'] = response_method
        print('send data')
        print(curruslt)
        try:
            socket.sender(curruslt)
        except:
            socket.close()
            time.sleep(1)
            print('file was not deleted!')
        shutil.rmtree(fpath,ignore_errors=True)



if __name__ == '__main__':
    exec_polqa_test()  #0 从头开始  #-1 从尾开始
