import zmq
import sys
import random
from utilities import *


def establishConnections(IP, start_port, process_count):
    
    temp_list = list(range(start_port,start_port+process_count))
    master_ports_list = list()

    while len(temp_list):
        rnd = random.randint(0,5000) % len(temp_list)
        master_ports_list.append(temp_list[rnd])
        temp_list.remove(master_ports_list[-1])
        
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
'''
master_IP="127.0.0.1"
master_start_port=40500
master_processes_count=10

context, socket_list, master_ports_list = establishConnections(
    master_IP, master_start_port, master_processes_count)

last_requested_server = 0

context = zmq.Context()
# DK_IP_port="127.0.0.1:5556"

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
        sent_message = {"PROCESS" : process}
        if process == "download":
            sent_message.update({"FILE_NAME" : file_name})

        master_ports_list[last_requested_server].send_pyobj(sent_message)
        DK_IP_port = master_ports_list[last_requested_server].recv_string()
        last_requested_server += 1

        temp_socket = context.socket(zmq.PAIR)
        temp_socket.connect("tcp://"+DK_IP_port)

        client_message = dict()

        if process == "upload":
            client_message = sendFile(file_name)
    
        client_message.update({
            "PROCESS_TYPE" : process,
            "FILE_NAME" : file_name
            })

        
        while client_message['FILE_NAME'].find('/') != -1:
            index=client_message['FILE_NAME'].find('/')
            size = len(client_message['FILE_NAME'])
            client_message['FILE_NAME']=client_message['FILE_NAME'][index+1:size]

        temp_socket.send_pyobj(client_message)

        if process == "download":
            received_message = temp_socket.recv_pyobj()
            
            while received_message['FILE_NAME'].find('/') != -1:
                index=received_message['FILE_NAME'].find('/')
                size = len(received_message['FILE_NAME'])
                received_message['FILE_NAME']=received_message['FILE_NAME'][index+1:size]
            
            saveFile(received_message)

            print("Downloading Done!")
        else:
            print("Uploading Done!")
        
        
        temp_socket.close()

        print("Want new process?[Y/n]",end='')
        choice = input()
        if choice =='n':
            break
        
        
    else:
        print("==========> Wrong process type!\n")