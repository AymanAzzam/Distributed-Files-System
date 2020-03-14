from zmq import EAGAIN
temp_dk = dict()


def alive(ip,port,alive_period, alive_table,available_stream_table,my_mutex):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.setsockopt(zmq.SUBSCRIBE, 'alive')
	sock.setsockopt(zmq.ZMQ_RCVTIMEO, 1)
	socket.bind('tcp://%s:%s'%(ip,port))

	while True:

		for k, v in alive_table.items():
			temp_dk[k] = "dead"


		while (val = socket.recv_pyobj() != -1):
			if (val['TOPIC'] == "alive"):
				temp_dk[val['IP']] = "alive"
			elif (val['TOPIC'] == "success"):
				my_mutex.acquire()
				available_stream_table[val["IP"]+":"+val["process_id"]]= "available" 
				my_mutex.release()
			else:
				print("Alive process got unexcpected topic")

		my_mutex.acquire()
		for k, v in temp_dk.items():
			alive_table[k] = v
		my_mutex.release()

		time.sleep(alive_period)
