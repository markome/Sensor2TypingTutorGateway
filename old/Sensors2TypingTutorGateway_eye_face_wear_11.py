# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 17:19:46 2016

@author: markome
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 10:02:19 2016
Facereader and Tobii eye tracker and AndroidWear 2 JS - python app. Creates 2 sockets for incomming dotNET app (from tobii and noldus) messages and forwards them on http as .json objects.
All received events (from tobi and noldus) are stored into buffer and send as vector upon http request. When data is sent, buffer is cleared.
For developmnet purposes, until no data is received from noldus and tobii the app is sending "placeholder" data repeatedly. Placeholder data is in format of actual data.
For ports and addresses and paths please see configuration variables.

call of http://localhost:8080/emptyData clears all data buffers.

!! Code requires bottle package.
Install python package bottle by issuing following command from cmd window:
pip install bottle

Code snippets were stollen from various sources:

Working solution from for CORS using bottle (Allow get requests from another server than JavaScript application is originating from):
http://stackoverflow.com/questions/17262170/bottle-py-enabling-cors-for-jquery-ajax-requests

Creation of json:
http://stackoverflow.com/questions/23110383/how-to-dynamically-build-a-json-object-with-python

Threading:
http://stackoverflow.com/questions/2846653/python-multithreading-for-dummies

@author: markome, marko.meza@fe.uni-lj.si
"""




import threading
import socket
import sys
import bottle
from bottle import response
import json
import time
import datetime



import re






























runTimestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')

#configuration of dotNET application communication socket - data source
global tobiiDotNetAppAddress
tobiiDotNetAddress = 'localhost'
global tobiiDotNeAppPort
tobiiDotNeAppPort=10003

tobiiEyeTrackerServerHostRoute='/tobiiEyetracker'

global tobiiEyeTrackerReceivedEventCounter
tobiiEyeTrackerReceivedEventCounter=0;

global receivedTobiiMessage
# default data sent UNTIL none is received from FaceReader
receivedTobiiMessage=[]
#receivedTobiiMessage.append(json.loads('{"tobiiEyeTracker": {"leftPos": {"y": "6,54191137932216","x": "-6,95598391113099","z": "58,852241687782"},"timeStamp": "24.12.2015 11:06:59.6288","leftGaze": {"y": "21,7719111544532","x": "0,86490466749226","z": "6,23850804784943"},"rightPos": {"y": "7,04664176343695","x": "-0,80637315236163","z": "59,3518039600174"},"rightGaze": {"y": "22,6628011052412","x": "-5,56592479836322","z": "6,56276625429384"}}}'))
#receivedTobiiMessage.append(json.loads('{"tobiiEyeTracker": {"leftPos": {"y": "6,54191137932216","x": "-6,95598391113099","z": "58,852241687782"},"timeStamp": "24.12.2015 11:06:59.6288","leftGaze": {"y": "21,7719111544532","x": "0,86490466749226","z": "6,23850804784943"},"rightPos": {"y": "7,04664176343695","x": "-0,80637315236163","z": "59,3518039600174"},"rightGaze": {"y": "22,6628011052412","x": "-5,56592479836322","z": "6,56276625429384"}}}'))
receivedTobiiMessage.append(json.loads('{"tobiiEyeTracker":{"timeStamp":"30.12.2015 14:06:20.2412","leftPos":{"x":"-0,228793755914194","y":"11,5027813555582","z":"60,912982163767"},"rightPos":{"x":"5,89524352818696","y":"11,2245013358383","z":"61,0730322352786"},"leftGaze":{"x":"3,15812377150551","y":"17,3247499470179","z":"4,61986983600664"},"rightGaze":{"x":"-2,49937069615642","y":"17,3932511520527","z":"4,64480229580618"},"leftPupilDiameter":"2,645874","rightPupilDiameter":"2,622345"}}'))
receivedTobiiMessage.append(json.loads('{"tobiiEyeTracker":{"timeStamp":"30.12.2015 14:06:20.2442","leftPos":{"x":"-0,258863875351471","y":"11,5149518687205","z":"60,9095247803002"},"rightPos":{"x":"5,88168331298095","y":"11,2362714331765","z":"61,0613078775579"},"leftGaze":{"x":"2,38144559635971","y":"16,7283881083418","z":"4,40281135417063"},"rightGaze":{"x":"-3,55454772939922","y":"17,2529816540119","z":"4,59374825056375"},"leftPupilDiameter":"2,642151","rightPupilDiameter":"2,673187"}}'))

global tobiiReceivedFromSender # this is used for debugging. Until actual data is received, fake data  is sent.
tobiiReceivedFromSender=False

global tobiiSocketRunning
tobiiSocketRunning = True
global tobiiDataLocalFileLogging
tobiiDataLocalFileLogging=True
global tobiiDataLocalFileLoggingFileName
tobiiDataLocalFileLoggingFileName='tobiiLog_'+runTimestamp+'.log'






global faceReaderDotNetAddress
faceReaderDotNetAddress='localhost'
global faceReaderDotNeAppPort
faceReaderDotNeAppPort=10001
#global noldusFaceReaderServerHostRoute
noldusFaceReaderServerHostRoute='/noldusFaceReader'
global noldusFaceReaderReceivedEventCounter
noldusFaceReaderReceivedEventCounter=0;
global receivedNoldusMessage
receivedNoldusMessage=[]
# default data sent UNTIL none is received from FaceReader
receivedNoldusMessage.append('DetailedLog 18.11.2015 14:41:35.299 Neutral : 0,5704 Happy : 0,6698 Sad : 0,0013 Angry : 0,0040 Surprised : 0,0129 Scared : 0,0007 Disgusted : 0,0048 Valence : 0,6650 Arousal : 0,2297 Gender : Male Age : 20 - 30 Beard : None Moustache : None Glasses : Yes Ethnicity : Caucasian Y - Head Orientation : -1,7628 X - Head Orientation : 2,5652 Z - Head Orientation : -3,0980 Landmarks : 375,4739 - 121,6879 - 383,2627 - 113,6502 - 390,8202 - 110,3507 - 396,1021 - 109,7039 - 404,9615 - 110,9594 - 443,2603 - 108,9765 - 451,9454 - 106,7192 - 457,1207 - 106,8835 - 464,1162 - 109,5496 - 470,9659 - 116,8992 - 387,4940 - 132,0171 - 406,4031 - 130,4482 - 441,6239 - 128,6356 - 460,6862 - 128,1997 - 419,0713 - 161,6479 - 425,3519 - 155,1223 - 431,9862 - 160,6411 - 406,9320 - 190,3831 - 411,4790 - 188,7656 - 423,1751 - 185,6583 - 428,5339 - 185,6882 - 433,7802 - 184,8167 - 445,6192 - 186,3515 - 450,8424 - 187,2787 - 406,0796 - 191,1880 - 411,9287 - 193,5352 - 417,9666 - 193,6567 - 424,0851 - 193,4941 - 428,6678 - 193,5652 - 433,2172 - 192,7540 - 439,3548 - 192,0136 - 445,4181 - 191,1532 - 451,6007 - 187,9486 - 404,5193 - 190,6352 - 412,8277 - 185,4609 - 421,1355 - 181,2883 - 428,3182 - 181,1826 - 435,2024 - 180,2258 - 443,9292 - 183,2533 - 453,1117 - 187,2288 - 405,9689 - 193,2750 - 410,0249 - 199,8118 - 416,0457 - 203,0374 - 423,4839 - 204,1818 - 429,9247 - 204,2175 - 436,3620 - 203,1305 - 443,4268 - 200,9355 - 448,9572 - 197,1335 - 452,0746 - 190,0314 Quality : 0,8137 Mouth : Closed Left Eye : Open Right Eye : Open Left Eyebrow : Lowered Right Eyebrow : Lowered Identity : NO IDENTIFICATION')
receivedNoldusMessage.append('DetailedLog    24.12.2015 13:01:54.282    ')
global noldusReceivedFromSender # this is used for debugging. Until actual data is received, fake data  is sent.
noldusReceivedFromSender=False
global noldusSocketRunning
noldusSocketRunning = True
global noldusDataLocalFileLogging
noldusDataLocalFileLogging=True
global noldusDataLocalFileLoggingFileName
noldusDataLocalFileLoggingFileName='noldusLog_'+runTimestamp+'.log'



global wearSocketRunning
wearSocketRunning = True
global wearSocketAddress


# !!!!!!!!!!!!!!!!!! if correct IP is obtained automatically leave like this. 
#Otherwise use commented IP hardcoding line
#wearSocketAddress="192.168.81.186"
wearSocketAddress=socket.gethostbyname(socket.gethostname())
global wearSocketPort
wearSocketPort=10005
global wearReceivedEventCounter
wearReceivedEventCounter=0
wearServerHostRoute='/wear'
global receivedWearMessage
receivedWearMessage=[]
#fake data for debugging
receivedWearMessage.append(json.loads('{"timestamp":"02.02.2016 09:36:55.0860","type":"accel","z":9.594614028930664,"y":0.1405097097158432,"x":0.07721300423145294}'))
receivedWearMessage.append(json.loads('{"timestamp":"02.02.2016 09:36:55.0930","type":"accel","z":9.592219352722168,"y":0.15487492084503174,"x":0.06763619929552078}'))

global wearReceivedFromSender # this is used for debugging. Until actual data is received, fake data  is sent.
wearReceivedFromSender=False
global wearDataLocalFileLogging
wearDataLocalFileLogging=True
global wearDataLocalFileLoggingFileName
wearDataLocalFileLoggingFileName='wearLog_'+runTimestamp+'.log'


#configuration of http server serving json
#serverHostIP = '192.168.81.76'
#serverHostIP = 'localhost'
serverHostIP = '127.0.0.1'
serverHostPort=8080

#call to this url clears all data buffers.
emptyDataServerHostRoute='/emptyData'

#global tobiiEyeTrackerServerHostRoute
#tobiiEyeTrackerServerHostRoute='/facereader'





# parses NOLDUS string to compatible JSON object (by David Brvar)

def parseNoldus(x):
    # da javasscript lahko lazje stringe spremeni v floate (rabi decimalno piko)
    zamenjajVseVejiceSPiko = re.compile('\,')    
    # compilan tu in ne v for loopu - za performance!
    parsajVJSONObjekt = re.compile(ur'(?:(DetailedLog) ([^ ]+ [^ ]+)|(\b[A-Z][A-Za-z -]+?) : ((?:(?:-?[\d.]+)(?: - -?[\d.]+)*|(?:(?:[A-Z ]+\b|[A-Za-z]+)))))(?:$| )')  
    data = []
    result = {}
    temp = {}  
    # obdela vsak posamezni element v listu
    for i in x:
        temp = zamenjajVseVejiceSPiko.sub(".", i)  
        # vse matche spravim v array
        temp = re.findall(parsajVJSONObjekt, temp)
        # obdela vsak match posebej, matchi so tipa <type 'tuple'>
        for match in temp:
            # sortiram glede na to, kako regex vrne matche
            if match[0]:
                result[match[0]] = match[1]
            else:
                result[match[2]] = match[3]
        data.append(result)
    return data






print 'LUCAMI gateway Noldus module starting.'
# Establiehses server socket for incomming connections from .net application.            
def listenNoldusFaceReaderSocketFromDotNET():
    #will run util this is True    
    global noldusSocketRunning    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    # Bind the socket to the port
    global faceReaderDotNetAddress
    global faceReaderDotNeAppPort
    server_address = (faceReaderDotNetAddress, faceReaderDotNeAppPort)
    print >>sys.stderr, 'Server socket for incomming data: starting up on %s port %s' % server_address
    sock.bind(server_address)
    
    global noldusDataLocalFileLogging
    #noldusDataLocalFileLogging=True
    global noldusDataLocalFileLoggingFileName
    #noldusDataLocalFileLoggingFileName='noldusLog_'+runTimestamp+'.log'
    
    # Listen for incoming connections
    sock.listen(1)
    
    while noldusSocketRunning:
        # Wait for a connection
        print >>sys.stderr, 'Server socket for incomming data: waiting for a connection'
        connection, client_address = sock.accept()
        
        try:
            print >>sys.stderr, 'Server socket for incomming data: connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while noldusSocketRunning:
                global noldusFaceReaderReceivedEventCounter
                noldusFaceReaderReceivedEventCounter = noldusFaceReaderReceivedEventCounter + 1
                global receivedNoldusMessage
                global noldusReceivedFromSender
                data = connection.recv(10000) # kinda ugly hack. If incomming message will be longer this will spill.
                #receivedNoldusMessage = data
                
                if (not noldusReceivedFromSender): #clear data
                    print 'Got first message from Tobii. Switching to real data mode.'
                    noldusReceivedFromSender = True
                    receivedNoldusMessage=[]
                    
                receivedNoldusMessage.append(data)
                if noldusDataLocalFileLogging:
                    f = open(noldusDataLocalFileLoggingFileName, 'a')                        
                    f.write(data)
                    f.close()
                #print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'Server socket for incomming data: sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'Server socket for incomming data: no more data from', client_address
                    break
                
        finally:
            # Clean up the connection
            connection.shutdown(1);
            connection.close()
            print 'Closing incomming data socket connection.'
    print 'Finished server socket for incomming data thread'
# start listening socket in thread
# About threads:  http://docs.python.org/2/library/threading.html#thread-objects
listeningNoldusSocketThread = threading.Thread(target=listenNoldusFaceReaderSocketFromDotNET, args=())
listeningNoldusSocketThread.start()





print 'LUCAMI gateway Tobii module starting.'

# Establiehses server socket for incomming connections from .net application.            
def listenTobiiSocketFromDotNET():
    #will run util this is True    
    global tobiiSocketRunning    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    # Bind the socket to the port
    global tobiiDotNetAddress
    global tobiiDotNeAppPort
    server_address = (tobiiDotNetAddress, tobiiDotNeAppPort)
    print >>sys.stderr, 'Server socket for incomming tobii data: starting up on %s port %s' % server_address
    sock.bind(server_address)
    
    global tobiiDataLocalFileLogging
    #tobiiDataLocalFileLogging=True
    global tobiiDataLocalFileLoggingFileName
    #tobiiDataLocalFileLoggingFileName='tobiiLog_'+runTimestamp+'.log'
    
    # Listen for incoming connections
    sock.listen(1)
    
    while tobiiSocketRunning:
        # Wait for a connection
        print >>sys.stderr, 'Server socket for incomming tobii data: waiting for a connection'
        connection, client_address = sock.accept()
        
        try:
            print >>sys.stderr, 'Server socket for incomming tobii data: connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while tobiiSocketRunning:
                global receivedTobiiMessage
                global tobiiEyeTrackerReceivedEventCounter
                tobiiEyeTrackerReceivedEventCounter=tobiiEyeTrackerReceivedEventCounter+1
                data = connection.recv(10000) # kinda ugly hack. If incomming message will be longer this will spill.
                #receivedTobiiMessage = data
                global tobiiReceivedFromSender
                if(not tobiiReceivedFromSender): #clear data
                    print 'Got first message from Noldus. Switching to real data mode.'
                    tobiiReceivedFromSender = True
                    receivedTobiiMessage=[]                
                try:
                    if tobiiDataLocalFileLogging:
                        f = open(tobiiDataLocalFileLoggingFileName, 'a')                        
                        f.write(data)
                        f.close()
                    receivedTobiiMessage.append(json.loads(data))
                except:
                    print 'Exception while parsing received JSON nessage from tobii'
                    if tobiiDataLocalFileLogging:
                        f = open(tobiiDataLocalFileLoggingFileName, 'a')
                        f.write('Exception while parsing received JSON nessage:')
                        f.write(data)
                        f.close()
                #receivedTobiiMessage.append(data)
                #print >>sys.stderr, 'received "%s"' % data
                if data:
                    print >>sys.stderr, 'Server socket for incomming tobii data: sending data back to the client'
                    connection.sendall(data)
                else:
                    print >>sys.stderr, 'Server socket for incomming tobii data: no more data from', client_address
                    break
                
        finally:
            # Clean up the connection
            connection.shutdown(1);
            connection.close()
            print 'Closing incomming tobii data socket connection.'
    print 'Finished server socket for incomming tobii data thread'
# start listening socket in thread
# About threads:  http://docs.python.org/2/library/threading.html#thread-objects
listeningTobiiSocketThread = threading.Thread(target=listenTobiiSocketFromDotNET, args=())

#print 'SOCKET SERVER NOT STARTED!!!!! Uncomment to start.'
listeningTobiiSocketThread.start()


print 'LUCAMI gateway Wear module starting.'

def listenWearSocket():
    #will run util this is True  
    global wearSocketRunning
     # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    # Bind the socket to the port
    global wearSocketAddress
    global wearSocketPort
    server_address = (wearSocketAddress, wearSocketPort)
    print >>sys.stderr, 'Server socket for incomming data: starting up on %s port %s' % server_address
    print >>sys.stderr, 'If you see error creating socket please hardcode ip in wearSocketAddress variable.'
    sock.bind(server_address)
    
    global wearDataLocalFileLogging
    #wearDataLocalFileLogging=True
    global wearDataLocalFileLoggingFileName
    #wearDataLocalFileLoggingFileName='wearLog.log'    
    
    
    # Listen for incoming connections
    sock.listen(1)
    while wearSocketRunning:
        # Wait for a connection
        print >>sys.stderr, 'Server socket for incomming data: waiting for a connection'
        connection, client_address = sock.accept()
        
        try:
            print >>sys.stderr, 'Server socket for incomming data: connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while wearSocketRunning:
                global wearReceivedEventCounter
                wearReceivedEventCounter = wearReceivedEventCounter + 1
                global receivedWearMessage
                global wearReceivedFromSender
                wearReceivedFromSender=True
                data = connection.recv(10000) # kinda ugly hack. If incomming message will be longer this will spill.
                #receivedNoldusMessage = data
                
                #if (not noldusReceivedFromSender): #clear data
                #    print 'Got first message from Tobii. Switching to real data mode.'
                #    noldusReceivedFromSender = True
                #    receivedNoldusMessage=[]
                    
                #receivedWearMessage.append(data)
                if wearDataLocalFileLogging:
                    f = open(wearDataLocalFileLoggingFileName, 'a')
                    f.write(data)
                    f.close()
                #fata ='{"timestamp":1454328042855,"z":1.1598410606384277,"y":1.7661726474761963,"x":-9.566631317138672}'
                #receivedWearMessage.append(json.loads(fata))
                try:
                    recv = json.loads(data)
                    receivedWearMessage.append(recv)
                    #receivedWearMessage.append(json.loads(data))
                except:
                    print 'Exception while parsing received JSON nessage from wear.'
                    if wearDataLocalFileLogging:
                        f = open(wearDataLocalFileLoggingFileName, 'a')
                        f.write('Exception while parsing received JSON nessage:')
                        f.write(data)
                        f.close()                        
                
                print >>sys.stderr, 'received "%s"' % data
                if data:
                    #print >>sys.stderr, 'Server socket for incomming data: sending data back to the client'
                    #connection.sendall(data)
                    print >>sys.stderr, 'Since lazy Marko did not implement it jet, NOT sending received data back to Android.'
                else:
                    print >>sys.stderr, 'Server socket for incomming data: no more data from', client_address
                    break
                
        finally:
            # Clean up the connection
            connection.shutdown(1);
            connection.close()
            print 'Closing incomming data socket connection.'
    print 'Finished server socket for incomming data thread'
# start listening socket in thread
# About threads:  http://docs.python.org/2/library/threading.html#thread-objects
listenWearSocketThread = threading.Thread(target=listenWearSocket, args=())
listenWearSocketThread.start() 


 
            
# In order to enable CORS - .JS getting data from another web address
# sourced from: http://stackoverflow.com/questions/17262170/bottle-py-enabling-cors-for-jquery-ajax-requests
class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)
        return _enable_cors


app = bottle.app()

#@app.route('/cors', method=['OPTIONS', 'GET'])
@app.route(tobiiEyeTrackerServerHostRoute, method=['OPTIONS', 'GET'])
def tobiiEyeTrackerResponder():
    response.headers['Content-type'] = 'application/json'
    #i=i+1
    global receivedTobiiMessage
    #i=i+1
    global tobiiEyeTrackerReceivedEventCounter
    data = {}
    #data['mykey']='myvalue'
    data['receivedEventCounter']=tobiiEyeTrackerReceivedEventCounter
    data['TobiiDetailedLog'] = receivedTobiiMessage
    json_data = json.dumps(data)
    #clear message buffer
    if tobiiReceivedFromSender:
        receivedTobiiMessage=[]
    else:
        print 'Sending emulated response for Tobii, since no data arrived jet from tobii.'
            
    #return '[1]'
    
    return json_data
    


@app.route(noldusFaceReaderServerHostRoute, method=['OPTIONS', 'GET'])
def noldusFaceReaderDataResponder():
    response.headers['Content-type'] = 'application/json'
    #i=i+1
    global noldusFaceReaderReceivedEventCounter
    global receivedNoldusMessage
    data = {}
    #data['mykey']='myvalue'
    data['receivedEventCounter']=noldusFaceReaderReceivedEventCounter
    data['NoldusDetailedLog'] = parseNoldus(receivedNoldusMessage)
    
    json_data = json.dumps(data)
    
    #clear message buffer
    if noldusReceivedFromSender:
        receivedNoldusMessage=[]
    else:
        print 'Sending emulated response for Noldus, since no data arrived jet from Noldus.'
    #return '[1]'
    
    return json_data
    
    
@app.route(wearServerHostRoute, method=['OPTIONS', 'GET'])
def wearDataResponder():
    response.headers['Content-type'] = 'application/json'
    #i=i+1
    global wearReceivedEventCounter
    global receivedWearMessage
    data = {}
    #data['mykey']='myvalue'
    data['receivedEventCounter']=wearReceivedEventCounter
    data['wearLog'] = receivedWearMessage
    json_data = json.dumps(data)
    #clear message buffer
    if wearReceivedFromSender:
        receivedWearMessage=[]
    else:
        print 'Sending emulated response for Wear, since no data arrived jet from Noldus.'
    #return '[1]'
    
    return json_data    
    
    
    
# clears all data buffers
@app.route(emptyDataServerHostRoute, method=['OPTIONS', 'GET'])
def emptyDataDataResponder():
    response.headers['Content-type'] = 'application/json'
    #i=i+1
    #global wearReceivedEventCounter
    global receivedWearMessage
    global receivedNoldusMessage
    global receivedTobiiMessage
    #data = {}
    #data['mykey']='myvalue'
    #data['receivedEventCounter']=wearReceivedEventCounter
    #data['wearLog'] = receivedWearMessage
    #json_data = json.dumps(data)
    #clear message buffer
    #if wearReceivedFromSender:
    #    receivedWearMessage=[]
    #else:
    #    print 'Sending emulated response for Wear, since no data arrived jet from Noldus.'
    print 'Clearing all data buffers.'    
    receivedWearMessage=[]
    receivedNoldusMessage=[]
    receivedTobiiMessage=[]
    return '[1]'
    
    #return json_data      
    
app.install(EnableCors())
print 'Starting http server on http://',serverHostIP,':',serverHostPort,tobiiEyeTrackerServerHostRoute
app.run(host=serverHostIP, port=serverHostPort)   

print 'Cleanup: http server stopped.'
print 'Cleanup: Stopping incomming tobii data socket server.'
tobiiSocketRunning = False
#send one last message to socket thread to disconnect. Ugly hack. Not working until other side client is connected.
tobiiClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tobiiServer_address = (tobiiDotNetAddress, tobiiDotNeAppPort)
tobiiClientSock.connect(tobiiServer_address)  
tobiiClientSock.sendall('Die!')
tobiiClientSock.close()

print 'Cleanup: Stopping incomming noldus data socket server.'
noldusSocketRunning = False
#send one last message to socket thread to disconnect. Ugly hack. Not working until other side client is connected.
noldusClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
noldusServer_address = (faceReaderDotNetAddress, faceReaderDotNeAppPort)
noldusClientSock.connect(noldusServer_address)  
noldusClientSock.sendall('Die!')
noldusClientSock.close()

print 'Cleanup: Stopping incomming wear data socket server.'
wearSocketRunning = False
#send one last message to socket thread to disconnect. Ugly hack. Not working until other side client is connected.
wearClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
wearServer_address = (wearSocketAddress, wearSocketPort)
wearClientSock.connect(wearServer_address)  
wearClientSock.sendall('Die!')
wearClientSock.close()

    
# this should finish the program. Currently does not work, since socket does not disconnect.
listeningTobiiSocketThread.join()
listeningNoldusSocketThread.join()
listenWearSocketThread.join()

