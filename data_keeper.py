import zmq
import sys
import os
from utilities import *
import signal


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


#heart beating::
def heart_beat (socket):
    data = {
        'topic' : topic_alive,
        'msg' : "Alive"
    }
    socket.send_pyobj(data)

#alarm handler::
def alarm_handler(sig, frame):
    heart_beat(publish_socket)
    signal.alarm(1)


#send success message after client upload data successfully::
def success_upload (socket,path,file,user):
    data = {
        'topic' : topic_success,
        'file_name' : file,
        'path' : path,
        'data_node_no' : (my_ip+':'+publish_port),
        'user_ID' : user
    }
    socket.send_pyobj(data)

dir_path='DATA'

if os.path.isdir(dir_path) == False:
    os.mkdir(dir_path)

signal.signal(signal.SIGALRM, alarm_handler)

#ATRRIB: IP STREAM_PORT PUBLISHER_REPORT NOTIFICATION_PORT
my_ip=sys.argv[1]
master_ip = sys.argv[5]

stream_port = sys.argv[2]
#publisher_port
publish_port = sys.argv[3]
#notification_port
subscriber_port = sys.argv[4]
#the process will send alive message or not
alive_sender = sys.argv[6]

#topics:
#alive topic : 
topic_alive = 0
#success topic :
topic_success = 1
#notifications topic :
topic_subscribe = my_ip + ':' + subscriber_port

context = zmq.Context()

stream = context.socket(zmq.PAIR)
#publisher socket:
publish_socket = context.socket(zmq.PUB)
#notification socket (subscriber)
subscriber_socket = context.socket(zmq.SUB)

#connections:
stream.bind("tcp://"+ my_ip +":" + str(stream_port))  ##note that:: stream port is actually string not integer
publish_socket.bind("tcp://%s:%s" %(my_ip,publish_port))
subscriber_socket.connect("tcp://%s:%s" %(master_ip,subscriber_port))
subscriber_socket.subscribe(topic_subscribe)


#heart beating:
if alive_sender == '1' :
    signal.alarm(1)

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
    
