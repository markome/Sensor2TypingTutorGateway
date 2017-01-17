# -*- coding: utf-8 -*-
"""
Created on Wen Nov 18 14:02:19 2015
Facereader 2 JS - python app. Creates socket for incomming dotNET app messages and forwards them on http as .json objects.
Currently only last form FR received message received is served


Working solution from for CORS using bottle
http://stackoverflow.com/questions/17262170/bottle-py-enabling-cors-for-jquery-ajax-requests

creation of json
http://stackoverflow.com/questions/23110383/how-to-dynamically-build-a-json-object-with-python

!! install package bottle
!! install package pyserial, currently (19.11.2015) it does not work under windows 10

@author: markome
"""


#http://stackoverflow.com/questions/2846653/python-multithreading-for-dummies
import threading
import socket
import sys
import bottle
from bottle import response
import json
import serial
import time
import datetime

#configuration of dotNET application communication socket
global faceReaderDotNetAppAddress
faceReaderDotNetAddress = 'localhost'
global faceReaderDotNeAppPort
faceReaderDotNeAppPort=10001

#configuration of http server serving json
global serverHostIP
serverHostIP = '192.168.81.76'
global serverHostPort
serverHostPort=8080
global serverHostRoute
serverHostRoute='/facereader'

#configuration of on serial port connected arduino sensor
global arduinoSensorSerialPort
arduinoSensorSerialPort='COM10'
global arduinoSensorSerialPortSpeed
arduinoSensorSerialPortSpeed=115200

#arduino sensor global variables.
global serialArduinoMessage
global readingArduinoSerial
readingArduinoSerial = True
serialMessage=''

global i
i=0;
global receivedFRMessage
# default data sent UNTIL none is received from FaceReader
receivedFRMessage = 'DetailedLog 18.11.2015 14:41:35.299 Neutral : 0,5704 Happy : 0,6698 Sad : 0,0013 Angry : 0,0040 Surprised : 0,0129 Scared : 0,0007 Disgusted : 0,0048 Valence : 0,6650 Arousal : 0,2297 Gender : Male Age : 20 - 30 Beard : None Moustache : None Glasses : Yes Ethnicity : Caucasian Y - Head Orientation : -1,7628 X - Head Orientation : 2,5652 Z - Head Orientation : -3,0980 Landmarks : 375,4739 - 121,6879 - 383,2627 - 113,6502 - 390,8202 - 110,3507 - 396,1021 - 109,7039 - 404,9615 - 110,9594 - 443,2603 - 108,9765 - 451,9454 - 106,7192 - 457,1207 - 106,8835 - 464,1162 - 109,5496 - 470,9659 - 116,8992 - 387,4940 - 132,0171 - 406,4031 - 130,4482 - 441,6239 - 128,6356 - 460,6862 - 128,1997 - 419,0713 - 161,6479 - 425,3519 - 155,1223 - 431,9862 - 160,6411 - 406,9320 - 190,3831 - 411,4790 - 188,7656 - 423,1751 - 185,6583 - 428,5339 - 185,6882 - 433,7802 - 184,8167 - 445,6192 - 186,3515 - 450,8424 - 187,2787 - 406,0796 - 191,1880 - 411,9287 - 193,5352 - 417,9666 - 193,6567 - 424,0851 - 193,4941 - 428,6678 - 193,5652 - 433,2172 - 192,7540 - 439,3548 - 192,0136 - 445,4181 - 191,1532 - 451,6007 - 187,9486 - 404,5193 - 190,6352 - 412,8277 - 185,4609 - 421,1355 - 181,2883 - 428,3182 - 181,1826 - 435,2024 - 180,2258 - 443,9292 - 183,2533 - 453,1117 - 187,2288 - 405,9689 - 193,2750 - 410,0249 - 199,8118 - 416,0457 - 203,0374 - 423,4839 - 204,1818 - 429,9247 - 204,2175 - 436,3620 - 203,1305 - 443,4268 - 200,9355 - 448,9572 - 197,1335 - 452,0746 - 190,0314 Quality : 0,8137 Mouth : Closed Left Eye : Open Right Eye : Open Left Eyebrow : Lowered Right Eyebrow : Lowered Identity : NO IDENTIFICATION'

global socketRunning
socketRunning = True



print 'LUCAMI gateway FaceReader2JS starting.'



#prints available serial ports on the machine
def printPortList():
    from serial.tools import list_ports 
    print "Available serial ports: "
    for a in list_ports.comports(): 
        print(a)

# reads message from serial port and stores it into global variable
# CHECK what happens if reading starts in the middle of line!!!! MIGHT CAUSE CRASHES!!!!
def readSerial(serialPort, serialPortSpeed):
    #ser = serial.Serial('COM10', 115200, timeout=0)
    ser = serial.Serial(serialPort, serialPortSpeed, timeout=0)
    global serialArduinoMessage 
    global readingArduinoSerial
    i=0
    while readingArduinoSerial:
        i=i+1
        #print "Reading RS232 in loop %d" % (i)
        try:
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y %H:%M:%S.%f')
            temp = ser.readline()
            serialArduinoMessage=timestamp + ' ' + temp            
            #print serialArduinoMessage
            time.sleep(0.01) #consider changing sampling rate...
        except ser.SerialTimeoutException:
            print('Data could not be read')
            time.sleep(0.1)
    ser.close()
    print 'Serial: read %d serial lines.' %(i)
    
#list available ports
printPortList()

#create and start serial socket thread
readSerialThread = threading.Thread(target=readSerial, args=(arduinoSensorSerialPort,arduinoSensorSerialPortSpeed))
readSerialThread.start()





# Establiehses server socket for incomming connections from .net application.            
def listenSocketFromDotNET():
    #will run util this is True    
    global socketRunning    
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    # Bind the socket to the port
    global faceReaderDotNetAddress
    global faceReaderDotNeAppPort
    server_address = (faceReaderDotNetAddress, faceReaderDotNeAppPort)
    print >>sys.stderr, 'Server socket for incomming data: starting up on %s port %s' % server_address
    sock.bind(server_address)
    
    # Listen for incoming connections
    sock.listen(1)
    
    while socketRunning:
        # Wait for a connection
        print >>sys.stderr, 'Server socket for incomming data: waiting for a connection'
        connection, client_address = sock.accept()
        
        try:
            print >>sys.stderr, 'Server socket for incomming data: connection from', client_address
    
            # Receive the data in small chunks and retransmit it
            while socketRunning:
                global receivedFRMessage
                global i
                i=i+1
                data = connection.recv(10000) # kinda ugly hack. If incomming message will be longer this will spill.
                receivedFRMessage = data
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
listeningSocketThread = threading.Thread(target=listenSocketFromDotNET, args=())
listeningSocketThread.start()

 
            
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
@app.route(serverHostRoute, method=['OPTIONS', 'GET'])
def lvambience():
    response.headers['Content-type'] = 'application/json'
    #i=i+1
    global i
    i=i+1
    global receivedFRMessage
    data = {}
    #data['mykey']='myvalue'
    data['counter']=i
    data['FaceReaderDetailedLog'] = receivedFRMessage
    data['ArduinoAccelSensorLog'] = serialArduinoMessage
    json_data = json.dumps(data)
    #return '[1]'
    
    return json_data
app.install(EnableCors())
#app.run(port=8001)
#app.run(host='192.168.81.76', port=8080)
print 'Starting http server on http://',serverHostIP,':',serverHostPort,serverHostRoute
app.run(host=serverHostIP, port=serverHostPort)   




print 'Cleanup: http server stopped.'
print 'Stopping serial thread'
readingArduinoSerial = False
print 'Cleanup: Stopping incomming data socket server.'
socketRunning = False
#send one last message to socket thread to disconnect. Ugly hack. Not working until other side client is connected.
clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (faceReaderDotNetAddress, faceReaderDotNeAppPort)
clientSock.connect(server_address)  
clientSock.sendall('Die!')
clientSock.close()
    
# this should finish the program. Currently does not work, since socket does not disconnect.
listeningSocketThread.join()

