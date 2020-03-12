import multiprocessing
from multiprocessing import Lock
import sys
import zmq
import random
import time

ip1 = "127.0.0.1";	port = int(sys.argv[1]);	n = int(sys.argv[2])
keepers_num = 0;	processes_num = 0
replica_factor = 3

lookup_table = multiprocessing.Manager().dict()
available_stream_table = multiprocessing.Manager().dict()
available_publish_table = multiprocessing.Manager().dict()
ports_list = multiprocessing.Manager().list()

class value:
	def __init__(self, user_id, datakeepers_list, paths_list):
		self.user_id= user_id
		self.datakeepers_list= datakeepers_list
		self.paths_list= paths_list

	def valPrint(self):
		print(self.user_id, self.datakeepers_list, self.paths_list)



def updateLookup(proc_num,filename, value):
	print("i am process numberrr : %i"  %proc_num)
	lookup_table[filename]=value


def printLookup(proc_num,lookup_table):
	print("i am process number : %i inside print"  %proc_num)
	for k, v in lookup_table.items():
		print(k)
		lookup_table[k].valPrint()

def printAvailable(proc_num):
	print("i am process number : %i inside print Available"  %proc_num)
	for k, v in available_stream_table.items():
		print(k, v)	

def configure():
	f = open("config.txt", "r")
	keepers_num = int(f.readline())
	processes_num = int(f.readline())
	for i in range(0,keepers_num):
		ip = f.readline().rstrip()			#.rstrip to erase "\n" from the ip end
		ip_port = int(f.readline())
		for j in range(0,processes_num):
			available_stream_table[ip+":"+str(ip_port+2*j)] = "available"
			available_publish_table[ip+":"+str(ip_port+2*j+1)] = "available"
			ports_list.append(ip+":"+str(ip_port+2*j))
	return keepers_num, processes_num

def keeper_for_replica(v):
	index = 0;	i = 0
	while True:
		i = 0;	flag = True
		while(i<len(v.datakeepers_list) and flag):
			if(v.datakeeper_list[i].split(":")[0] == ports_list[index].split(":")[0]):
				flag = False
			i = i + 1
		if(flag):
			break
		index = index + processes_num
	return index

def start_index_for_ip(ip):
	index = 0
	while(ip != ports_list[index].split(":")[0]):
		index = index + 1
	return index

def src_dst_port(v):
	dst_index_start = keeper_for_replica(v);	dst_index = dst_index_start
	my_mutex.acquire()
	while(available_stream_table[ports_list[dst_index]] == 'busy'):	#Get available destination port for source to connect on it
		dst_index = (dst_index + 1) % (dst_index_start + processes_num)
	available_stream_table[ports_list[dst_index]] = 'busy'
	
	src_index_start = start_index_for_ip(v.datakeeper_list[i].split(":")[0]);	src_index = src_index_start
	while(available_stream_table[ports_list[src_index]] == 'busy'):	#Get available source port for master to connect on it
		src_index = (src_index + 1) % (src_index_start + processes_num)
	available_stream_table[ports_list[src_index]] = 'busy'
	my_mutex.release()
	return src_index, dst_index

def notify_src_dst(socket1,socket2,k,src_index,dst_index):
	src_ip =  ports_list[src_index].split(":")[0];	src_port_stream = ports_list[src_index].split(":")[1]
	dst_ip =  ports_list[dst_index].split(":")[0];	dst_port_stream = ports_list[dst_index].split(":")[1]
	src_port_notification = src_port_stream;	dst_port_notification = dst_port_stream

	message_src = {'NODE_TYPE': "source", 'FILE_NAME': k, 'IP': dst_ip, 'PORT': dst_port_stream}
	message_dst = {'NODE_TYPE': "destination"}
	socket1.connect("tcp://%s:%s"%(dst_ip,dst_port_notification))
	socket1.send_pyobj(message_dst)
	socket1.disconnect()
	socket2.connect("tcp://%s:%s"%(src_ip,src_port_notification))
	socket2.send_pyobj(message_src)
	socket2.disconnect()
	
def replica():
	context = zmq.Context()
	socket1 = context.socket(zmq.PAIR)
	socket2 = context.socket(zmq.PAIR)

	while True:
		for k, v in lookup_table.items():
			i = 0;	j = 0
			while(len(v.datakeepers_list)< replica_factor):
				src_index, dst_index = src_dst_port(v)
				notify_src_dst(socket1,socket2,k,src_index,dst_index)
				replica_factor = replica_factor + 1
		time.sleep(1)

def master_client(port1):
	my_id = random.randrange(10000)
	starting_dk_port_index = random.randrange(keepers_num*processes_num)

	context = zmq.Context()
    
	client = context.socket(zmq.REP)            #REP because it needs to receive then send
	client.bind("tcp://%s:%i"%(ip1,port1))      #client will connect to this port

	while True:
		data = client.recv_pyobj()              #Receive message from client 
		
		#receiving dictionary contains command(upload/download) and file(file_Data for upload/file_name for download)
		print("master_client_id %i received command type %s" %(my_id, data['PROCESS']))
		

		if(data['PROCESS']=="upload"):
			my_mutex.acquire()
			while(available_stream_table[ports_list[starting_dk_port_index]] == "busy"):
				starting_dk_port_index=(starting_dk_port_index+1)%(keepers_num*processes_num)
			available_stream_table[ports_list[starting_dk_port_index]] = "busy"
			my_mutex.release()
			client.send_string(ports_list[starting_dk_port_index])

		elif(data['PROCESS']=="download"):
			val = lookup_table[data['FILE_NAME']]
			datakeeper_list= val.datakeepers_list
			my_mutex.acquire()
			ip_index_temp = start_index_for_ip(datakeeper_list[0].split(":")[0]);	ip_index = ip_index_temp
			while(available_stream_table[ports_list[ip_index]] == "busy"):
				ip_index = (ip_index + 1) % (ip_index + processes_num)
			available_stream_table[ports_list[ip_index]] = "busy"
			my_mutex.release()
			client.send_string(ports_list[ip_index])	

		else:
			print("master_client_id %i received invalid command" %(my_id))

if __name__ == "__main__":
	with multiprocessing.Manager() as manager:
		my_mutex = Lock()
		my_id = random.randrange(10000)

		keepers_num, processes_num = configure()
		
		p = []
		for i in range(0,n):
			p.append(multiprocessing.Process(target=master_client, args=(port,)))
			p[i].start()
			port = port + 1

		for i in range(0,n):
			p[i].join()
