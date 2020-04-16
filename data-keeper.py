import zmq
import sys
import os
import time
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

            print("Download Request...")

            #Message verification
            if ("FILE_NAME") not in message:
                raise NameError("File name is missed!")
            
            print("["+message['USER_ID']+"] requested to download: " + message['FILE_NAME'])
            print("Preparing file to stream...")
            message['FILE_NAME'] = data_path+'/'+message['FILE_NAME']
            sent_message = sendFile(message['FILE_NAME'])
            
            stream_socket.send_pyobj(sent_message)

            print("File streamed successfully!")

            #send success message to master:
            success_download(publisher_socket,process)
            

        elif process == "upload":

            print("Upload request...")

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
            

            print("["+message['USER_ID']+"] requested to upload: " + message['FILE_NAME'])
            print("File is being saved...")
            message['FILE_NAME'] = data_path+'/'+message['FILE_NAME']
            saveFile(message)

            print("File saved successfully!")

            #send success message to master:
            success_upload(publisher_socket,process,message['USER_ID'],message['FILE_NAME'].split("/")[-1])
            

        else:
            raise NameError("Error in streaming!")





    def processReplicate(message, stream_socket, context, publisher_socket):
        if message['NODE_TYPE'] == "source":

            print("Replica Request. I'm source...")

            #Message verification
            if ("FILE_NAME") not in message:
                raise NameError("File name is missed!")
        
            if ("IP") not in message:
                raise NameError("IP is missed")

            if ("PORT") not in message:
                raise NameError("PORT is missed")

            if ("USER_ID") not in message:
                raise NameError("User ID is missed")

            time.sleep(2)
            destination_socket = context.socket(zmq.PAIR)
            destination_socket.connect("tcp://" + message['IP'] + ":" + message['PORT'])

            print("Replica: source sending: " + message['FILE_NAME'])
            print("Preparing file to stream...")

            sent_message = sendFile(message['FILE_NAME'])

            sent_message.update({'USER_ID' : message['USER_ID']})

            print("source sending message to "+"tcp://" + message['IP'] + ":" + message['PORT']+"...")
            destination_socket.send_pyobj(sent_message)
            destination_socket.close()
            print("source done")

            print("File streamed successfully!")

            #send success to master:
            success_download(publisher_socket,message['NODE_TYPE'])



        elif message['NODE_TYPE'] == "destination":

            print("Replica Request. I'm destination...")

            received_file = stream_socket.recv_pyobj()
            
            print("Replica: destination receiving: " + received_file['FILE_NAME'])
            print("File is being saved...")
            received_file['FILE_NAME'] = data_path+"/"+received_file['FILE_NAME']
            saveFile(received_file)

            print("File saved successfully!")
            #send success to master:
            success_upload (publisher_socket,message['NODE_TYPE'],received_file['USER_ID'],received_file['FILE_NAME'].split("/")[-1])

        else:
            raise NameError("Error in Node Type")


    #heart beating::
    def heart_beat (socket):
        data = {
            'TOPIC' : topic_alive,
            'IP' : my_ip,
            'PROCESS_ID' : process_id
        }
        socket.send_pyobj(data)

    #alarm handler::
    def alarm_handler(signum=None, frame=None):
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
        print("Downloading done!\n")

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
        print("Uploading done!\n")

    ########################################=>MAIN<=########################################


    #####SIGNAL####
    signal.signal(signal.SIGALRM, alarm_handler)
    
    #stream_port (streaming / notifications)
    stream_port = process_id
    #publisher_port (heart beating / success messages)
    publish_port = stream_port + 1

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
    if heart_beating_process == True :
        signal.alarm(1)

    while True:
        message = stream_socket.recv_pyobj()
        if ("PROCESS_TYPE") in message:
            processStream(message,stream_socket,publish_socket)
            print("Press any key to teriminate the data keeper!\n")
        elif ("NODE_TYPE") in message:
        	print("my connection is "+"tcp://"+ my_ip +":" + str(stream_port)+"...")
        	processReplicate(message, stream_socket, context, publish_socket)
        	print("Press any key to teriminate the data keeper!\n")
        else:
            raise NameError("Process type is missed!\n")

########################=>MAIN_PROCESS<=########################

'''
Attributes:
    MY_STARTING_PORT
    PROCESSES_NUM
    DATA_PATH
'''

my_ip = sys.argv[1]
data_path = sys.argv[4]

if __name__ == "__main__":
    current_port = int(sys.argv[2])
    processes_num = int(sys.argv[3])

    print("Initiating a Datakeepr...")

    if os.path.isdir(data_path) == False:
        os.mkdir(data_path)
    
    print("Data Folder... Done!")

    processes_list = list()
    for i in range(0,processes_num):
        processes_list.append(multiprocessing.Process(
            target=main,args=(current_port,(i==0),)))
        processes_list[-1].daemon = True    # To terminate the child process once the parent terminated
        processes_list[-1].start()
        print("Process " + str(current_port) + " started!")
        current_port += 2

    print("Press any key to teriminate the data keeper!\n")
    ch = input()
    # for process in processes_list:
    #     if process.is_alive() == True:
    #         process.terminate()