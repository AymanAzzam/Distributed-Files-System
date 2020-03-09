import multiprocessing
import sys
import zmq
import random

ip1 = "127.0.0.1";	port = int(sys.argv[1]);	n = int(sys.argv[2])
keepers_num = 0;	processes_num = 0

lookup_table = multiprocessing.Manager().dict()
available_table = multiprocessing.Manager().dict()
ports_list = multiprocessing.Manager().list()

def updateLookup(proc_num,filename, value):
	print("i am process numberrr : %i"  %proc_num)
	lookup_table[filename]=value


def printLookup(proc_num):
	print("i am process number : %i inside print Lookup"  %proc_num)
	for k, v in lookup_table.items():
		print(k, v)

def printAvailable(proc_num):
	print("i am process number : %i inside print Available"  %proc_num)
	for k, v in available_table.items():
		print(k, v)	

def configure():
	f = open("config.txt", "r")
	keepers_num = int(f.readline())
	processes_num = int(f.readline())
	for i in range(0,keepers_num):
		ip = f.readline().rstrip()			#.rstrip to erase "\n" from the ip end
		ip_port = int(f.readline())
		for j in range(0,processes_num):
			available_table[ip+"/"+str(ip_port+j)] = "available"
			ports_list.append(ip+"/"+str(ip_port+j))

def master_client(port1):
	my_id = random.randrange(10000)
    
	context = zmq.Context()
    
	client = context.socket(zmq.REP)            #REP because it needs to receive then send
	client.bind("tcp://%s:%i"%(ip1,port1))      #client will connect to this port

	while True:
		data = client.recv_pyobj()              #Receive message from client 
		#receiving dictionary contains command(upload/download) and file(file_Data for upload/file_name for download)
		print("master_client_id %i received command type %s" %(my_id, data['command']))
		
		if(data[command]=="upload"):
			print("5")
		elif(data[command]=="download"):
			print("6")
		else:
			print("master_client_id %i received invalid command" %(my_id))

if __name__ == "__main__":
	with multiprocessing.Manager() as manager:
		my_id = random.randrange(10000)

		configure()
		#printAvailable(my_id)
		
		for i in range(0,n):
			p1=	multiprocessing.Process(target=master_client, args=(port,))
			p1.start()
			port = port + 1