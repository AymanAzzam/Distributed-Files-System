import zmq
import sys
import random

ip1 = "127.0.0.1";  port1 = sys.argv[1]
#port1 = 5556
ip2 = "127.0.0.1";  port2 = 5558

def main():
    my_id = random.randrange(10000)
    
    context = zmq.Context()
    
    client = context.socket(zmq.REP)            #REP because it needs to receive then send
    client.bind("tcp://%s:%s"%(ip1,port1))      #client will connect to this port

    while True:
        data = client.recv_pyobj()              #Receive message from client 
        #receiving dictionary contains command(upload/download) and file(file_Data for upload/file_name for download)
        print("master_client_id %i received command type %s" %(my_id, data['command']))
        

main()