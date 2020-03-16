import zmq
from zmq import EAGAIN
import multiprocessing
from multiprocessing import Event
import time
import random
from print_tables import *
from utilities import *


def alive(ip,port,alive_period, alive_table,lookup_table,available_stream_table,ports_list,my_mutex_stream,my_mutex_lookup,my_mutex_alive,stop_event):
	my_id = random.randrange(10000)
	
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.bind('tcp://%s:%s'%(ip,port))
	socket.subscribe("")
	socket.setsockopt(zmq.RCVTIMEO, 100)

	temp_dk = dict()
	
	for k, v in alive_table.items():
		temp_dk[k] = "dead"

	while True:

		while True: 
			try:
				val = socket.recv_pyobj()
				#print( rec , "recieved" )
			except zmq.error.Again as e:
				#print('Alived rrrrece timed out ')
				continue	
			
			if (val['TOPIC'] == "alive"):
				temp_dk[val['IP']] = "alive"
			elif (val['TOPIC'] == "success"):
				my_mutex_stream.acquire()
				available_stream_table[val["IP"]+":"+val["PROCESS_ID"]]= "available" 
				my_mutex_stream.release()
				if (val['NODE_TYPE'] == "destination"):
					my_mutex_lookup.acquire()
					lookup_table[val['FILE_NAME']].datakeepers_list.append(val['IP']+":"+start_index_for_ip(val['IP'],ports_list)) 
					lookup_table[val['FILE_NAME']].user_id =val['USER_ID']
					lookup_table[val['FILE_NAME']].paths_list.append(val['FILE_NAME'])
					my_mutex_lookup.release()
			else:
				print("Alive process got unexcpected topic")

			if stop_event.is_set():
				stop_event.clear()
				break

		my_mutex_alive.acquire()
		for k, v in temp_dk.items():
			alive_table[k] = v
		my_mutex_alive.release()
		printAlive(my_id,alive_table)
		time.sleep(0.5)

def alive_helper(ip,port,alive_period, alive_table,lookup_table,available_stream_table,ports_list,my_mutex_stream,my_mutex_lookup,my_mutex_alive):
		# Event object used to send signals from one thread to another
		stop_event = Event()

		alive_thread = multiprocessing.Process(target=alive, args=(ip,port,alive_period, alive_table,lookup_table,available_stream_table,ports_list,my_mutex_stream,my_mutex_lookup,my_mutex_alive,stop_event))
		alive_thread.start()
		
		while True:
			time.sleep(0.25)
			stop_event.set()

		alive_thread.join()			

