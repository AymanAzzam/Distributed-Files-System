import time
import zmq
from utilities import *

def keeper_for_replica(v,ports_list,processes_num):
	index = 0;	i = 0
	while True:
		i = 0;	flag = True
		while(i<len(v.datakeepers_list) and flag):
			#TODO
			#Check here also if this data keeper is alive
			if(v.datakeepers_list[i].split(":")[0] == ports_list[index].split(":")[0]):
				flag = False
			i = i + 1
		if(flag):
			break
		index = index + processes_num
	return index

def src_dst_port(v,alive_table,available_stream_table,ports_list,processes_num,my_mutex):
	dst_index_start = keeper_for_replica(v,ports_list,processes_num);	dst_index = dst_index_start
	my_mutex.acquire()
	print("Master searching about available port for replica destination\n")
	while(available_stream_table[ports_list[dst_index]] == 'busy' or alive_table[ports_list[starting_dk_port_index].split(":")[0]] == "dead"):	#Get available destination port for source to connect on it
		dst_index = (dst_index + 1) % (dst_index_start + processes_num)
	print("Master got %s for replica destination\n"%(ports_list[starting_dk_port_index]))	
	available_stream_table[ports_list[dst_index]] = 'busy'
	
	print("Master searching about available port for replica source\n")
	src_index_start = start_index_for_ip(v.datakeepers_list[i].split(":")[0],ports_list);	src_index = src_index_start
	while(available_stream_table[ports_list[src_index]] == 'busy' or alive_table[ports_list[starting_dk_port_index].split(":")[0]] == "dead"):	#Get available source port for master to connect on it
		src_index = (src_index + 1) % (src_index_start + processes_num)
	print("Master got %s for replica source\n"%(ports_list[starting_dk_port_index]))	
	available_stream_table[ports_list[src_index]] = 'busy'
	my_mutex.release()
	return src_index, dst_index,dst_index_start

def notify_src_dst(socket1,socket2,k,src_index,dst_index,ports_list, user_id):
	src_ip =  ports_list[src_index].split(":")[0];	src_port_stream = ports_list[src_index].split(":")[1]
	dst_ip =  ports_list[dst_index].split(":")[0];	dst_port_stream = ports_list[dst_index].split(":")[1]
	src_port_notification = src_port_stream;	dst_port_notification = dst_port_stream

	message_src = {'NODE_TYPE': "source", 'FILE_NAME': k, 'IP': dst_ip, 'PORT': dst_port_stream, 'USER_ID' : user_id}
	message_dst = {'NODE_TYPE': "destination"}
	socket1.connect("tcp://%s:%s"%(dst_ip,dst_port_notification))
	socket1.send_pyobj(message_dst)
	print("Master sent messgae to replica destination\n")
	socket1.disconnect()
	socket2.connect("tcp://%s:%s"%(src_ip,src_port_notification))
	socket2.send_pyobj(message_src)
	print("Master sent messgae to replica source\n")
	socket2.disconnect()

def replica(replica_factor, replica_period, alive_table,lookup_table,available_stream_table,ports_list,processes_num,my_mutex):
	context = zmq.Context()
	socket1 = context.socket(zmq.PAIR)
	socket2 = context.socket(zmq.PAIR)
	#replica_factor = 3

	if(len(ports_list)/processes_num<replica_factor):
		return

	while True:
		#TODO
		#You have to convert the below part to a procedure to deal with in (alive.py line:57)
		for k, v in lookup_table.items():
			i = 0;	j = 0
			while(len(v.datakeepers_list)< replica_factor):
				src_index, dst_index,dst_index_start = src_dst_port(v,alive_table,available_stream_table,ports_list,processes_num,my_mutex)
				user_id = v.user_id
				notify_src_dst(socket1,socket2,k,src_index,dst_index,ports_list,user_id)
				# v.datakeepers_list.append(ports_list[dst_index_start])	# append the starting port for destination datakeeper on that file
		time.sleep(replica_period)