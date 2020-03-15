import zmq
from zmq import EAGAIN
import multiprocessing
from multiprocessing import Event
import time


temp_dk = dict()

def alive(ip,port,alive_period, alive_table,available_stream_table,my_mutex,stop_event):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.bind('tcp://%s:%s'%(ip,port))
	socket.subscribe("")
	socket.setsockopt(zmq.RCVTIMEO, 100)
	
	for k, v in alive_table.items():
		temp_dk[k] = "dead"

	while True:

		while True: 
			try:
				val = socket.recv_pyobj();
				#print( rec , "recieved" )
			except zmq.error.Again as e:
				print('test failed, answer timed out ')
				continue	
			
			if (val['TOPIC'] == "alive"):
				temp_dk[val['IP']] = "alive"
			elif (val['TOPIC'] == "success"):
				my_mutex.acquire()
				available_stream_table[val["IP"]+":"+val["process_id"]]= "available" 
				my_mutex.release()
			else:
				print("Alive process got unexcpected topic")

			if stop_event.is_set():
				stop_event.clear()
				break

		my_mutex.acquire()
		for k, v in temp_dk.items():
			alive_table[k] = v
		my_mutex.release()
 		


	

def alive_helper(ip,port,alive_period, alive_table,available_stream_table,my_mutex):
		# Event object used to send signals from one thread to another
		stop_event = Event()

		alive_thread = multiprocessing.Process(target=alive, args=(ip,port,alive_period, alive_table,available_stream_table,my_mutex,stop_event))
		alive_thread.start()
		
		while True:
			time.sleep(0.25)
			stop_event.set()

		alive_thread.join()			

