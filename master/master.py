import zmq
import sys
import random

ip1 = "127.0.0.1";  port1 = 5558


def main():
    my_id = random.randrange(10000)
    
    context = zmq.Context()

    client = context.socket(zmq.REP)        #REP because it needs to receive then send
    client.bind("tcp://%s:%s"%(ip1,port1))  #master_client process will connect on this port 

    while True:
        data = client.recv_pyobj()          #Get message from client_interact(processes that interact with the client)
        #receiving dictionary contains command(upload/download) and file(file_Data for upload/file_name for download)
        print("master_id %i received command type %s" %(my_id, data['command']))
        reply = "done"                   
        client.send_pyobj(reply)            #Send reply to client_interact process

main()