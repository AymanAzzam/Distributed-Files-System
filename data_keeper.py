import zmq
import sys
import os
from utilities import *
import signal
import multiprocessing


'''
download:
    *Request: FILE_NAME
    *Response: FILE_NAME, FPS, FOURCC, WIDTH, HEIGHT, COUNT, #0, #1, ..., #[COUNT-1]

upload:
    *Request: FILE_NAME, FPS, FOURCC, WIDTH, HEIGHT, COUNT, #0, #1, ..., #[COUNT-1]
'''
def main(process_id,heart_beating_process):

    def processStream(message, stream_socket, publisher_socket):

        process = message['PROCESS_TYPE']

        if process == "download":
            #Message verification
            if ("FILE_NAME") not in message:
                raise NameError("File name is missed!")
            
            message['FILE_NAME'] = data_path+'/'+message['FILE_NAME']
            sent_message = sendFile(message['FILE_NAME'])
            
            stream_socket.send_pyobj(sent_message)
            
            #send success message to master:
            # success_download(publisher_socket,process)


        elif process == "upload":
            #Message verification
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
            
            message['FILE_NAME'] = data_path+'/'+message['FILE_NAME']
            saveFile(message)

            #send success message to master:
            # success_upload(publisher_socket,process,message['USER_ID'],message['FILE_NAME'])

        else:
            raise NameError("Error in streaming!")





    def processReplicate(message, stream_socket, context, publisher_socket):
        
        if message['NODE_TYPE'] == "source":
            #Message verification
            if ("FILE_NAME") not in message:
                raise NameError("File name is missed!")
        
            if ("IP") not in message:
                raise NameError("IP is missed")

            if ("PORT") not in message:
                raise NameError("PORT is missed")
                
            destination_socket = context.socket(zmq.PAIR)
            destination_socket.connect("tcp://" + message['IP'] + ":" + message['PORT'])

            sent_message = sendFile(message['FILE_NAME'])

            destination_socket.send_pyobj(sent_message)
            destination_socket.close()
            
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

    ########################################=>MAIN<=########################################
    #####SIGNAL####
    # signal.signal(signal.SIGALRM, alarm_handler)

    #ATRRIB: IP STREAM_PORT PUBLISHER_REPORT HEART_BEATING_PROCESS
    #stream_port (streaming / notifications)
    stream_port = int(process_id)
    # stream_port = "5556"
    #publisher_port (heart beating / success messages)
    publish_port = stream_port + 1
    #the process will send alive message or not
    # heart_beating_process = sys.argv[3]

    #topics:
    #alive topic : 
    topic_alive = "alive"
    #success topic :
    topic_success = "success"

    context = zmq.Context()

    #streamer socket
    stream_socket = context.socket(zmq.PAIR)
    #publisher socket:
    publish_socket = context.socket(zmq.PUB)


    #connections:
    stream_socket.bind("tcp://"+ my_ip +":" + str(stream_port))
    publish_socket.bind("tcp://%s:%s" %(my_ip,str(publish_port)))

    #####SIGNAL####
    #heart beating:
    # if heart_beating_process == True :
    #     signal.alarm(1)

    while True:
        message = stream_socket.recv_pyobj()
        if ("PROCESS_TYPE") in message:
            processStream(message,stream_socket,publish_socket)
        elif ("NODE_TYPE") in message:
            processReplicate(message, stream_socket, context, publish_socket)
        else:
            raise NameError("Process type is missed!")

########################=>MAIN_PROCESS<=########################

my_ip = sys.argv[1]
data_path = sys.argv[4]

if __name__ == "__main__":
    current_port = int(sys.argv[2])
    processes_num = int(sys.argv[3])

    if os.path.isdir(data_path) == False:
        os.mkdir(data_path)
    
    processes_list = list()
    for i in range(0,processes_num):
        processes_list.append(multiprocessing.Process(
            target=main,args=(current_port,(i==0),)))
        processes_list[-1].daemon = True    # To terminate the child process once the parent terminated
        processes_list[-1].start()
        print("Process " + str(current_port) + " started!")
        current_port += 2

    print("Press any key to teriminate the data keeper!")
    ch = input()
    # for process in processes_list:
    #     if process.is_alive() == True:
    #         process.terminate()
