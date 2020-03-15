from zmq import EAGAIN
import zmq
from threading import Thread, Event, Timer
import time




temp_dk = dict()
# Event object used to send signals from one thread to another
stop_event = Event()


def alive(ip,port,alive_period, alive_table,available_stream_table,my_mutex):
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.setsockopt(zmq.SUBSCRIBE, 'alive')
	socket.bind('tcp://%s:%s'%(ip,port))

	for k, v in alive_table.items():
		temp_dk[k] = "dead"

			
	while ( True): 

		val = socket.recv_pyobj();
		if (val['TOPIC'] == "alive"):
			temp_dk[val['IP']] = "alive"
		elif (val['TOPIC'] == "success"):
			my_mutex.acquire()
			available_stream_table[val["IP"]+":"+val["process_id"]]= "available" 
			my_mutex.release()
		else:
			print("Alive process got unexcpected topic")

		if stop_event.is_set():
            break
 		


	

def alive_helper(ip,port,alive_period, alive_table,available_stream_table,my_mutex):
    # We create another Thread
	while True:	
		number = 3
		alive_thread = Thread(target=alive, args=(ip,port,alive_period, alive_table,available_stream_table,my_mutex))
	 
	    # Here we start the thread and we wait 5 seconds before the code continues to execute.
		alive_thread.start()
		alive_thread.join(timeout=0.5)
	 
	    # We send a signal that the other thread should stop.
		stop_event.set()
		
		my_mutex.acquire()
		for k, v in temp_dk.items():
			alive_table[k] = v
		my_mutex.release()

		print("Hey there! I timed out! You can do things after me!")	

			

