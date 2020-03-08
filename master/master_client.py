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

    master = context.socket(zmq.REQ)            #REQ because it needs to send then receive
    master.connect("tcp://%s:%s"%(ip2,port2))   #master process will bind on this port 
    
    while True:
        data = client.recv_pyobj()              #Receive message from client 
        #receiving dictionary contains command(upload/download) and file(file_Data for upload/file_name for download)
        print("master_client_id %i received command type %s" %(my_id, data['command']))
        master.send_pyobj(data)                 #Send the received message to the client
        reply = master.recv_pyobj()             #Get a reply from the master
        client.send_pyobj(reply)                #Send the reply to the client

main()