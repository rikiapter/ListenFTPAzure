from ftplib import FTP
from time import sleep
import requests 
import urllib.parse, urllib.request, json, ssl, xmltodict
import base64
import sys
from io import StringIO
import datetime
try:
    import ssl
except ImportError:
    _SSLSocket = None
else:
    _SSLSocket = ssl.SSLSocket


ftp = FTP('00.00.00.00')
ftp.login(user='*******', passwd = '********')
ftp.set_pasv(False)

def get_response(url, data, method='GET'):
    #try:
        assert(method in ('GET', 'POST'))
        if method == 'GET':
            encode_data = urllib.parse.urlencode(data)
            req = urllib.request.Request(f'{url}?{encode_data}', headers={'content-type': 'application/json'})
            response = urllib.request.urlopen(req)
        elif method == 'POST':
            params = json.dumps(data)
            binary_data = params.encode('utf8')
            req = urllib.request.Request(url
                                , data= binary_data
                                , headers={'content-type': 'application/json'})
            response = urllib.request.urlopen(req)
        x = response.read()
        return x
    #except:
    #    print(datetime.datetime.now() ,'ERROR get_response')

def changemon(dir='./'):
        old_files = ftp.nlst(dir) 
        print('old_files' + str(len(old_files)))
        while True:
            try:
                new_files = ftp.nlst(dir)
                #print('new_files' + str(len(new_files)))
                if new_files != old_files:
                    print(datetime.datetime.now() ,'New Files' + str(len(new_files)))
                    changes = [i for i in new_files if i not in old_files]
                    add = changes
                    if add: yield add

                    old_files = new_files
                sleep(0.1)
            except:
                print("ERROR changemon : ", sys.exc_info()[1])
                print("ERROR changemon : ", sys.exc_info()[2])
                #[WinError 10053] An established connection was aborted by the software in your host machine
                #
                sleep(2)
                #raise
def sendImage(s):
    #try:
        #print(datetime.datetime.now() ,'start send image ')
        _base64 =base64.b64encode(s)
        #print(str(_base64)[2:-1])
        url = f'https://malammastpenfacerecognitionazure.azurewebsites.net/api/v1/FaceRecognition/identify'
        data =    {
                            'image' : str(_base64)[2:-1],
                            'imageType' : 'base64',
                            'personGroupId' : 'facegroup1'
                }
        res_identify=get_response(url, data, method='POST')
        if res_identify!='':
            data = json.loads(res_identify)
            print (datetime.datetime.now() , data['dIdError'])

            if data['dIdError'] == False:
                if len(data['model']) > 0:
                    if len(data['model'][0]['candidates']) > 0:
                        #print(data['model'][0]['candidates'][0]['personId'])
                        url = f'https://malammastpenrealtimeapi20190626012828.azurewebsites.net/api/v1/EmployeeEntry/Entry'
                        data =    {
                                'EquipmentId' : 1,
                                'EmployeeFacePrintID' : data['model'][0]['candidates'][0]['personId']
                            }
                        res_identify=get_response(url, data, method='POST')
                        data = json.loads(res_identify)
                        print (datetime.datetime.now() , data['message'])
    #except:
    #    print(datetime.datetime.now() ,'ERROR sendImage')

def binary( cmd, callback, blocksize=8192, rest=None):
        #print(datetime.datetime.now() ,'start binary')
        string = ''
        data1 = bytes(string, 'utf-8')
        ftp.voidcmd('TYPE I')
        with ftp.transfercmd(cmd, rest) as conn:
            while 5:
                #print(datetime.datetime.now() ,'while')
                data = conn.recv(blocksize)
                if not data:
                    break
                else:
                    data1 = data1 + data
            callback(data1)
            # shutdown ssl layer
            if _SSLSocket is not None and isinstance(conn, _SSLSocket):
                conn.unwrap()
        return ftp.voidresp()



for add in changemon():
    for i in add:
            
            #print(datetime.datetime.now() , i.replace('./', ''))
            while True:
                try:
                    print(datetime.datetime.now() ,'TRY '+ i)
                    #sleep(2)
                    binary('RETR '+ i.replace('./', ''), sendImage,600000)# i 2019-12-16_13_21_46_id54655_obj45272.jpeg
                    print(datetime.datetime.now() ,'END TRY '+ i)
                #    ftp.quit()
                    break
                except IOError as e:
                    print("RETR SLEEP IOError error:", format(e)+ '  ' + i)
                    #[WinError 10054] An existing connection was forcibly closed by the remote host
                    # must sleep
                    sleep(2)
                    #break
                except:
                    print("RETR Unexpected error:", sys.exc_info()[1])
                    print("RETR Unexpected error:", sys.exc_info()[2])
                    sleep(0.1)
                    #break
                    #raise

ftp.quit()





