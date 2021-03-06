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


'''
Attributes:
    MASTER_IP
    MASTER_START_PORT
    MASTER_PROCESSES_COUNT
    DOWNLOAD_DIR
    USER_ID
'''
master_IP=sys.argv[1]
master_start_port=int(sys.argv[2])
master_processes_count=int(sys.argv[3])
download_dir = sys.argv[4]
user_id = sys.argv[5]

last_requested_server = 0

if os.path.isdir(download_dir) == False:
    os.mkdir(download_dir)


context, master_socket_list, master_ports_list = establishConnections(
    master_IP, master_start_port, master_processes_count)


context = zmq.Context()

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
        master_message = {"PROCESS" : process}
        if process == "download":
            master_message.update({"FILE_NAME" : file_name})

        master_process = master_socket_list[last_requested_server]
        master_process.send_pyobj(master_message)

        master_received = master_process.recv_pyobj()
        
        if ("FILE_NAME" in master_received):
            print ("File name invalid\n")
            continue
        else:
            DK_IP_port = master_received['IP'] + ":" + master_received['PORT']
        last_requested_server += 1
        last_requested_server %= master_processes_count
        print("Client got ip:port %s\n"%(DK_IP_port))

        #Establishing connection to a data keeper 
        DK_socket = context.socket(zmq.PAIR)
        DK_socket.connect("tcp://"+DK_IP_port)

        DK_message = dict()

        if process == "upload":
            DK_message = sendFile(file_name)
            file_name=DK_message['FILE_NAME'].split("/")[-1]
    
        
        DK_message.update({
            "PROCESS_TYPE" : process,
            "FILE_NAME" : file_name,
            "USER_ID" : user_id
            })

        DK_socket.send_pyobj(DK_message)

        if process == "download":
            received_message = DK_socket.recv_pyobj()

            received_message['FILE_NAME'] = download_dir + '/' + received_message['FILE_NAME'].split("/")[-1]
            saveFile(received_message)

            print("Downloading Done!\n")
        else:
            print("Uploading Done!\n")
        
        
        DK_socket.close()

        print("Want new process?[Y/n]   ",end='')
        choice = input()
        if choice =='n' or choice =='N':
            break    
        
    else:
        print("==========> Wrong process type!\n")