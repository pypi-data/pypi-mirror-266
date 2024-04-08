from socket import *
import threading
import json
import os,time

address='10.219.36.124'
port=2159
buffsize=1024
s = socket(AF_INET, SOCK_STREAM)
s.bind((address,port))
s.listen(100)     #max connect
conn_list = []
conn_dt = {}
requeststack = {}

cur_server_name = 'serverB'
cur_server_name_2 = 'serverC'
request_method = 'request'
response_method = 'response'



def tcplink(sock,addr):
    while True:
        time.sleep(1)
        try:
            recvdata=sock.recv(buffsize).decode('utf-8')
            curdic = json.loads(recvdata)
            # client
            if curdic['module'] == 'clientA' and curdic['method'] == 'requestA':
                timeout = 30
                if 'timeOut' in curdic:
                    timeout = curdic['timeOut']
                if 'server' not in curdic:
                    cur_server = 'random'
                else:
                    if curdic['server'] != cur_server_name and curdic['server'] != cur_server_name_2:
                        cur_server = 'random'
                    else:
                        cur_server = curdic['server']
                requeststack[curdic['token']] = [0,'',[curdic['srcFile'],curdic['testFile'],curdic['samplerate']],cur_server,'No error']
                n = 0
                while True:
                    time.sleep(1)
                    n += 1
                    if n >= timeout:
                        oneitem = requeststack.pop(curdic['token'])
                        curdic['result'] = {'delay':'No Result','mos':'-0.0','Speech Level Gain':'','Noise Level Gain':'','err':'Time out'}
                        curdic['server'] = oneitem[3]
                        curdic['err'] = 'Time out'
                        sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                        os.system("rm -rf /home/netease/polqa/" + curdic['token'])
                        break
                    if requeststack[curdic['token']][1] != '':
                        oneitem = requeststack.pop(curdic['token'])
                        curdic['result'] = oneitem[1]
                        curdic['server'] = oneitem[3]
                        curdic['err'] = oneitem[4]
                        sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                        os.system("rm -rf /home/netease/polqa/" + curdic['token'])
                        break
            # request
            if (curdic['module'] == cur_server_name and curdic['method'] == request_method) or (curdic['module'] == cur_server_name_2 and curdic['method'] == request_method):
                if len(requeststack) != 0:
                    for onekey in requeststack:
                        if requeststack[onekey][0] == 0:
                            cur_server = requeststack[onekey][3]
                            if cur_server == 'random':
                                requeststack[onekey][3] = curdic['module']
                                requeststack[onekey][0] = 1
                                curdic['token'] =  onekey
                                curdic['job'] = 'occupy'
                                curdic['srcFile'] = requeststack[onekey][2][0]
                                curdic['testFile'] = requeststack[onekey][2][1]
                                curdic['samplerate'] = requeststack[onekey][2][2]
                                sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                            else:
                                if curdic['module'] == cur_server:
                                    requeststack[onekey][0] = 1
                                    curdic['token'] = onekey
                                    curdic['job'] = 'occupy'
                                    curdic['srcFile'] = requeststack[onekey][2][0]
                                    curdic['testFile'] = requeststack[onekey][2][1]
                                    curdic['samplerate'] = requeststack[onekey][2][2]
                                    sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                                else:
                                    curdic['job'] = None
                                    sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                            break
                    else:
                        curdic['job'] = None
                        sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
                else:
                    curdic['job'] = None
                    sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
            #
            if curdic['module'] == cur_server_name and curdic['method'] == response_method:
                #
                #if curdic['err'] == 'No error':
                requeststack[curdic['token']][1] = curdic['result']
                requeststack[curdic['token']][3] = cur_server_name
                requeststack[curdic['token']][4] = curdic['err']
                sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
            if curdic['module'] == cur_server_name_2 and curdic['method'] == response_method:
                #
                #if curdic['err'] == 'No error':
                requeststack[curdic['token']][1] = curdic['result']
                requeststack[curdic['token']][3] = cur_server_name_2
                requeststack[curdic['token']][4] = curdic['err']
                sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
            if not recvdata:
                break
        except:
            sock.close()
            print(addr,'offline')
            _index = conn_list.index(addr)
            conn_dt.pop(addr)
            conn_list.pop(_index)
            break

def recs():
    while True:
        clientsock,clientaddress=s.accept()
        if clientaddress not in conn_list:
            conn_list.append(clientaddress)
            conn_dt[clientaddress] = clientsock
        print('connect from:',clientaddress)
        #
        t=threading.Thread(target=tcplink,args=(clientsock,clientaddress))
        t.start()

if __name__ == '__main__':
    t1 = threading.Thread(target=recs, args=(), name='rec')

    t1.start()

