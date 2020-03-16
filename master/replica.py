import time
import zmq
from utilities import *
from print_tables import *

def keeper_for_replica(v,ports_list,processes_num):
	index = 0;	i = 0
	printPortList(1,ports_list)
	print(processes_num)
	while True:
		i = 0;	flag = True
		while(i<len(v.datakeepers_list) and flag):
			#TODO
			#Check here also if this data keeper is alive
			if(v.datakeepers_list[i] == ports_list[index]):
				flag = False
			i = i + 1
		if(flag):
			break
		index = (index + processes_num)%len(ports_list)
	return index

def src_dst_port(v,alive_table,available_stream_table,ports_list,processes_num,my_mutex):
	dst_index_start = keeper_for_replica(v,ports_list,processes_num)
	my_mutex.acquire()
	print("Master searching about available port for replica destination\n")


	offset = 0
	dst_index = dst_index_start

	ip = ports_list[dst_index].split(":")[0]
	base_port = datakeeperFirstPort(ip,ports_list[dst_index].split(":")[1],alive_table)

	while(available_stream_table[ports_list[dst_index]] == 'busy' or alive_table[ip+":"+base_port] == "dead"):	#Get available destination port for source to connect on it
		offset = (offset + 1) % (processes_num)
		dst_index = offset + dst_index_start

	print("Master got %s for replica destination\n"%(ports_list[dst_index]))	
	available_stream_table[ports_list[dst_index]] = 'busy'
	
	print("Master searching about available port for replica source\n")
	src_index_start = start_index_for_ip(v.datakeepers_list[0],processes_num,ports_list)
	offset = 0
	src_index = src_index_start
	while(available_stream_table[ports_list[src_index]] == 'busy' or alive_table[ports_list[src_index_start]] == "dead"):	#Get available source port for master to connect on it
		offset = (offset + 1) % (processes_num)
		src_index = offset + src_index_start

	print("Master got %s for replica source\n"%(ports_list[src_index]))	
	available_stream_table[ports_list[src_index]] = 'busy'
	my_mutex.release()
	return src_index, dst_index

def notify_src_dst(context,k,src_index,dst_index,ports_list, user_id,lookup_table,available_stream_table,alive_table,my_mutex_lookup,my_mutex_stream):
	src_ip =  ports_list[src_index].split(":")[0];	src_port_stream = ports_list[src_index].split(":")[1]
	dst_ip =  ports_list[dst_index].split(":")[0];	dst_port_stream = ports_list[dst_index].split(":")[1]
	src_port_notification = src_port_stream;	dst_port_notification = dst_port_stream

	notification_sub_socket = context.socket(zmq.SUB)

	notification_sub_socket.connect("tcp://%s:%s"%(dst_ip,str(int(dst_port_notification)+1)))
	notification_sub_socket.connect("tcp://%s:%s"%(src_ip,str(int(src_port_notification)+1)))

	notification_sub_socket.subscribe("")
	
	socket1 = context.socket(zmq.PAIR)
	socket2 = context.socket(zmq.PAIR)
	message_src = {'NODE_TYPE': "source", 'FILE_NAME': k, 'IP': dst_ip, 'PORT': dst_port_stream, 'USER_ID' : user_id}
	message_dst = {'NODE_TYPE': "destination"}
	socket1.connect("tcp://%s:%s"%(dst_ip,dst_port_notification))
	socket1.send_pyobj(message_dst)
	print("Master sent messgae to replica destination\n")
	socket1.close()
	socket2.connect("tcp://%s:%s"%(src_ip,src_port_notification))
	socket2.send_pyobj(message_src)
	print("Master sent messgae to replica source\n")
	socket2.close()

	
	
	success_count = 0

	while success_count<2:
		
		val = notification_sub_socket.recv_pyobj()
	
		if (val['TOPIC'] == "success"):

			if(val['TYPE'] == "upload" or val['TYPE'] == "download"):
				continue

			my_mutex_stream.acquire()
			available_stream_table[val["IP"]+":"+str(val["PROCESS_ID"])]= "available" 
			my_mutex_stream.release()
			if (val['TYPE'] == "source"):
				print("Source done\n")

			elif (val['TYPE'] == "destination"):
				my_mutex_lookup.acquire()
				lookup_table[val['FILE_NAME']].datakeepers_list.append(val['IP']+":"+datakeeperFirstPort(val['IP'],val['PROCESS_ID'],alive_table))
				lookup_table[val['FILE_NAME']].paths_list.append(val['FILE_NAME'])
				my_mutex_lookup.release()
				print("Destination done\n")
			success_count += 1
	
	notification_sub_socket.close()



def replica(replica_factor, replica_period, alive_table,lookup_table,available_stream_table,ports_list,processes_num,my_mutex,my_mutex_lookup):
	context = zmq.Context()
	#replica_factor = 3

	if(len(ports_list)/processes_num<replica_factor):
		return

	while True:
		#TODO
		#You have to convert the below part to a procedure to deal with in (alive.py line:57)
		for k, v in lookup_table.items():
			i = 0;	j = 0
			while(len(v.datakeepers_list)< replica_factor):
				src_index, dst_index = src_dst_port(v,alive_table,available_stream_table,ports_list,processes_num,my_mutex)
				user_id = v.user_id
				notify_src_dst(context,k,src_index,dst_index,ports_list,user_id,lookup_table,available_stream_table,alive_table,my_mutex_lookup,my_mutex)
				# v.datakeepers_list.append(ports_list[dst_index_start])	# append the starting port for destination datakeeper on that file
		time.sleep(replica_period)
