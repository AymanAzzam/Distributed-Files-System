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

def processStream(message, stream_socket, publisher_socket):
    if ("PROCESS_TYPE") not in message:
        raise NameError("Error in streaming!")
    
    process = message['PROCESS_TYPE']

    if process == "download":
    
        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")

        message['FILE_NAME'] = dir_path+'/'+message['FILE_NAME']
        sent_message = sendFile(message['FILE_NAME'])
        
        stream_socket.send_pyobj(sent_message)
        
        #send success message to master:
        success_download(publisher_socket,process)


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

        #send success message to master:
        success_upload(publisher_socket,process,message['USER_ID'],message['FILE_NAME'])

    else:
        raise NameError("Error in streaming!")





def processReplicate(message, stream_socket, context, publisher_socket):
    if ("NODE_TYPE") not in message:
        raise NameError("Node type is missed!")

    
    if message['NODE_TYPE'] == "source":

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
        
        #send success to master:
        success_download(publisher_socket,message['NODE_TYPE'])


    elif message['NODE_TYPE'] == "destination":

        received_file = stream_socket.recv_pyobj()
        saveFile(received_file)

        #send success to master:
        success_upload (publisher_socket,message['NODE_TYPE'],message['USER_ID'],message['FILE_NAME'])

    else:
        raise NameError("Error in Node Type")


#heart beating::
def heart_beat (socket):
    data = {
        'TOPIC' : topic_alive,
        'IP' : my_ip
    }
    socket.send_pyobj(data)

#alarm handler::
def alarm_handler(sig, frame):
    heart_beat(publish_socket)
    signal.alarm(1)


#send success message after client download/src replicate data successfully::
def success_download (socket,notification):
    data = {
        'TOPIC' : topic_success,
        'IP' : my_ip,
        'PROCESS_ID' : process_id,
        'TYPE' : notification
    }
    socket.send_pyobj(data)

#send success message after client upload/destination replicate data successfully::
def success_upload (socket,notification,user,file_name):
    data = {
        'TOPIC' : topic_success,
        'IP' : my_ip,
        'PROCESS_ID' : process_id,
        'TYPE' : notification,
        'USER_ID' : user,
        'FILE_NAME' : file_name
    }
    socket.send_pyobj(data)

########################################=>MAIN<=###########################################
dir_path='DATA'

if os.path.isdir(dir_path) == False:
    os.mkdir(dir_path)

signal.signal(signal.SIGALRM, alarm_handler)

#ATRRIB: IP STREAM_PORT PUBLISHER_REPORT HEART_BEATING_PROCESS
my_ip = sys.argv[1]
process_id = sys.argv[2]
#stream_port (streaming / notifications)
stream_port = int(process_id)
#publisher_port (heart beating / success messages)
publish_port = stream_port + 1
#the process will send alive message or not
heart_beating_process = sys.argv[3]

#topics:
#alive topic : 
topic_alive = "alive"
#success topic :
topic_success = "success"

context = zmq.Context()

stream_socket = context.socket(zmq.PAIR)
#publisher socket:
publish_socket = context.socket(zmq.PUB)
#notification socket (subscriber)
notifiction_socket = context.socket(zmq.PAIR)

#connections:
stream_socket.bind("tcp://"+ my_ip +":" + str(stream_port))
publish_socket.bind("tcp://%s:%s" %(my_ip,str(publish_port)))


#heart beating:
if heart_beating_process == '1' :
    signal.alarm(1)

while True:
    try:
        message = stream_socket.recv_pyobj(zmq.DONTWAIT)
        if ("PROCESS_TYPE") in message:
            processStream(message,stream_socket,publish_socket)
        else:
            processReplicate(message, stream_socket, context, publish_socket)
    except zmq.Again:
        pass
    
