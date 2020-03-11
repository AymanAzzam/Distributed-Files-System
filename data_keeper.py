import zmq
import sys
import os
from utilities import *


'''
download:
    *Request: FILE_NAME
    *Response: FILE_NAME, FPS, FOURCC, WIDTH, HEIGHT, COUNT, #0, #1, ..., #[COUNT-1]

upload:
    *Request: FILE_NAME, FPS, FOURCC, WIDTH, HEIGHT, COUNT, #0, #1, ..., #[COUNT-1]
'''

def processStream(message, socket):
    if ("PROCESS_TYPE") not in message:
        raise NameError("Error in streaming!")
    
    process = message['PROCESS_TYPE']

    if process == "download":
    
        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")

        message['FILE_NAME'] = dir_path+'/'+message['FILE_NAME']
        sent_message = sendFile(message['FILE_NAME'])
        
        socket.send_pyobj(sent_message)
        '''
        #TODO
        Here notify the master with the successful download
        '''


    elif process == "upload":
        
        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")

        if ("FPS") not in message:
            raise NameError("FPS is missed!")
        if ("FOURCC") not in message:
            raise NameError("FOURCC is missed!")
        if ("WIDTH") not in message:
            raise NameError("WIDTH is missed!")
        if ("HEIGHT") not in message:
            raise NameError("HEIGHT is missed!")
        if ("COUNT") not in message:
            raise NameError("COUNT is missed!")

        count = message['COUNT']

        for index in range(count):
            if ("#"+str(index)) not in message:
                raise NameError("frame #"+str(index)+" is missed!")
        
        message['FILE_NAME'] = dir_path+'/'+message['FILE_NAME']
        saveFile(message)

        '''
        #TODO
        Here notify the master with the successful upload
        '''

    else:
        raise NameError("Error in streaming!")





def processReplicate(message, socket, context):
    if ("NODE_TYPE") not in message:
        raise NameError("Node type is missed!")

    
    if message['NODE_TYPE'] == "Source":

        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")
    
        if ("IP") not in message:
            raise NameError("IP is missed")

        if ("PORT") not in message:
            raise NameError("PORT is missed")
            
        temp_socket = context.socket(zmq.PAIR)
        temp_socket.connect("tcp://" + message['IP'] + ":" + message['PORT'])

        sent_message = sendFile(message['FILE_NAME'])

        temp_socket.send_pyobj(sent_message)
        temp_socket.close()
        
        '''
        #TODO
        Here notify the master with the successful Sending in replication
        '''


    elif message['NODE_TYPE'] == "Destination":

        received_file = socket.recv_pyobj()
        saveFile(received_file)

        '''
        #TODO
        Here notify the master with the successful Receiving in replication
        '''
    else:
        raise NameError("Error in Node Type")




dir_path='DATA'

if os.path.isdir(dir_path) == False:
    os.mkdir(dir_path)


#ATRRIB: IP STREAM_PORT PUBLISHER_REPORT NOTIFICATION_PORT
my_ip = sys.argv[1]
# my_ip="127.0.0.1"

stream_port = sys.argv[2]
# stream_port = 5556

#publisher_port here

context = zmq.Context()

stream = context.socket(zmq.PAIR)
#publisher socket here

stream.bind("tcp://"+ my_ip +":" + str(stream_port))
#publisher bind here

# print("I'm here")
while True:
    try:
        message = stream.recv_pyobj(zmq.DONTWAIT)
        processStream(message,stream)
    except zmq.Again:
        pass

    '''
    #TODO
    [ONLY RUN ON THE FIRST NODE]
    Heart beats are sent here
    '''

    '''
    #TODO
    #When receiving Replicate notification
    processReplicate(message, stream, context)
    '''
