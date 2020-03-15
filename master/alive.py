from zmq import EAGAIN
import zmq
from threading import Timer

import rzmq


temp_dk = dict()
def timeout():
	raise Exception("Time out")


def alive(ip,port,alive_period, alive_table,available_stream_table,my_mutex):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.setsockopt(zmq.SUBSCRIBE, 'alive')
	#socket.setsockopt(zmq.RCVTIMEO, 1) 
	socket.bind('tcp://%s:%s'%(ip,port))

	while True:

		for k, v in alive_table.items():
			temp_dk[k] = "dead"

		flag = True ##need to solve later

			
	while ( socket.recv_pyobj() ): 
		print("inside loop")
		'''
		errno = zmq.errno()
		if errno == EAGAIN:
			print("Got EAGAIN Error")
			raise Again(errno)
			
		val = socket.recv_pyobj();	flag = False
		if (val['TOPIC'] == "alive"):
			temp_dk[val['IP']] = "alive"
		elif (val['TOPIC'] == "success"):
			my_mutex.acquire()
			available_stream_table[val["IP"]+":"+val["process_id"]]= "available" 
			my_mutex.release()
		else:
			print("Alive process got unexcpected topic")
	errno = zmq.errno()
	if errno == EAGAIN:
		print("Got EAGAIN Error")
		raise Again(errno)
		'''

	my_mutex.acquire()
	for k, v in temp_dk.items():
		alive_table[k] = v
	my_mutex.release()

	time.sleep(alive_period)

			

