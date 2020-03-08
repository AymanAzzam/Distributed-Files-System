import zmq
import sys
import random

ip1 = "127.0.0.1";  port1 = int(sys.argv[1]);    n = int(sys.argv[2]);    file_path = sys.argv[3]

def main():
    my_id = random.randrange(10000)
    
    context = zmq.Context()

    master = context.socket(zmq.REQ)                    #REQ because it needs to send then receive    
    for i in range(0,n):
        master.connect("tcp://%s:%i"%(ip1,port1+i))     #master process will bind on this port
    
    #while True:                                        #commented for now but will need it later
    data = {}
    data['command'] = "upload"; data["file"] = "video.mp4"
    for i in range(6):
        master.send_pyobj(data)                         #Send data to the master
        print(master.recv_pyobj())                      #receive data from the master
    
main()
