import zmq
import sys
import os
import random
from utilities import *


def establishConnections(IP, start_port, process_count):
    
    temp_port_list = list(range(start_port,start_port+process_count))
    master_ports_list = list()

    #Randomizing connection sequence
    while len(temp_port_list):
        rnd = random.randint(0,5000) % len(temp_port_list)
        master_ports_list.append(temp_port_list[rnd])
        temp_port_list.remove(master_ports_list[-1])
        
    context = zmq.Context()
    socket_list = list()
    for port in master_ports_list:
        temp_socket = context.socket(zmq.REQ)
        temp_socket.connect("tcp://"+IP+":"+str(port))
        socket_list.append(temp_socket)
    
    return context, socket_list, master_ports_list


#user_id

# user_id = sys.argv[1]

'''
From File:
    MASTER_IP
    MASTER_START_PORT
    MASTER_PROCESSES_COUNT
    DOWNLOAD_DIR
'''
# master_IP="127.0.0.1"
# master_start_port=40500
# master_processes_count=10
download_dir = "Download"
# last_requested_server = 0

if os.path.isdir(download_dir) == False:
    os.mkdir(download_dir)


# context, socket_list, master_ports_list = establishConnections(
#     master_IP, master_start_port, master_processes_count)


context = zmq.Context()
# DK_IP_port = "127.0.0.1:5556"
DK_PORT=sys.argv[1]
DK_IP_port = "127.0.0.1:"+DK_PORT

while True:
    print("Enter Process type: ", end='')
    process = input()
    print('')

    if process == "exit":
        break

    if process == "download" or process == "upload":
        
        print("==>Enter File Name: ",end='')
        file_name = input()
        print('')

        #Preparing message sent to master
        # master_message = {"PROCESS" : process}
        # if process == "download":
        #     master_message.update({"FILE_NAME" : file_name})

        # master_process = master_ports_list[last_requested_server]
        # master_process.send_pyobj(master_message)

        # DK_IP_port = master_process.recv_string()
        # last_requested_server += 1

        #Establishing connection to a data keeper 
        DK_socket = context.socket(zmq.PAIR)
        DK_socket.connect("tcp://"+DK_IP_port)

        DK_message = dict()

        if process == "upload":
            DK_message = sendFile(file_name)
    
        DK_message.update({
            "PROCESS_TYPE" : process,
            "FILE_NAME" : file_name
            })

        
        while DK_message['FILE_NAME'].find('/') != -1:
            index=DK_message['FILE_NAME'].find('/')
            size = len(DK_message['FILE_NAME'])
            DK_message['FILE_NAME']=DK_message['FILE_NAME'][index+1:size]

        DK_socket.send_pyobj(DK_message)

        if process == "download":
            received_message = DK_socket.recv_pyobj()
            
            while received_message['FILE_NAME'].find('/') != -1:
                index=received_message['FILE_NAME'].find('/')
                size = len(received_message['FILE_NAME'])
                received_message['FILE_NAME']=received_message['FILE_NAME'][index+1:size]
            
            received_message['FILE_NAME'] = download_dir + '/' + received_message['FILE_NAME']
            saveFile(received_message)

            print("Downloading Done!")
        else:
            print("Uploading Done!")
        
        
        DK_socket.close()

        print("Want new process?[Y/n]",end='')
        choice = input()
        if choice =='n':
            break
        
        
    else:
        print("==========> Wrong process type!\n")