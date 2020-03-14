import time

def keeper_for_replica(v,ports_list,processes_num):
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

def start_index_for_ip(ip,ports_list):
	index = 0
	while(ip != ports_list[index].split(":")[0]):
		index = index + 1
	return index

def src_dst_port(v,alive_table,available_stream_table,ports_list,processes_num,my_mutex):
	dst_index_start = keeper_for_replica(v,ports_list,processes_num);	dst_index = dst_index_start
	my_mutex.acquire()
	while(available_stream_table[ports_list[dst_index]] == 'busy' or alive_table.[ports_list[starting_dk_port_index].split(":")[0]] == "dead"):	#Get available destination port for source to connect on it
		dst_index = (dst_index + 1) % (dst_index_start + processes_num)
	available_stream_table[ports_list[dst_index]] = 'busy'
	
	src_index_start = start_index_for_ip(v.datakeeper_list[i].split(":")[0],ports_list);	src_index = src_index_start
	while(available_stream_table[ports_list[src_index]] == 'busy' or alive_table.[ports_list[starting_dk_port_index].split(":")[0]] == "dead"):	#Get available source port for master to connect on it
		src_index = (src_index + 1) % (src_index_start + processes_num)
	available_stream_table[ports_list[src_index]] = 'busy'
	my_mutex.release()
	return src_index, dst_index,dst_index_start

def notify_src_dst(socket1,socket2,k,src_index,dst_index,ports_list):
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

def replica(replica_factor, replica_period, alive_table,lookup_table,available_stream_table,ports_list,processes_num,my_mutex):
	context = zmq.Context()
	socket1 = context.socket(zmq.PAIR)
	socket2 = context.socket(zmq.PAIR)
	#replica_factor = 3



	while True:
		for k, v in lookup_table.items():
			i = 0;	j = 0
			while(len(v.datakeepers_list)< replica_factor):
				src_index, dst_index,dst_index_star = src_dst_port(v,alive_table,available_stream_table,ports_list,processes_num,my_mutex)
				notify_src_dst(socket1,socket2,k,src_index,dst_index,ports_list)
				v.datakeepers_list.append(ports_list[dst_index_start])	# append the starting port for destination datakeeper on that file
		time.sleep(replica_period)