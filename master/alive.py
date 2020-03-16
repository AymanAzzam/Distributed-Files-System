import zmq
from zmq import EAGAIN
import multiprocessing
from multiprocessing import Event
import time
import random
from print_tables import *
from utilities import *
from main import value


def alive(ip,port,alive_period, alive_table,lookup_table,available_stream_table,ports_list,my_mutex_stream,my_mutex_lookup,my_mutex_alive):
	my_id = random.randrange(10000)
	
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	# socket.bind('tcp://%s:%s'%(ip,port))
	for ent in ports_list:
		ip = ent.split(":")[0]
		port = str(int(ent.split(":")[1])+1)
		socket.connect('tcp://%s:%s'%(ip,port))
	socket.subscribe("")
	socket.setsockopt(zmq.RCVTIMEO, 0)

	temp_dk = dict()
	
	for k, v in alive_table.items():
		temp_dk[k] = "dead"

	while True:

		while True: 
			try:
				val = socket.recv_pyobj()
			except zmq.error.Again as e:
				#print('Alived rrrrece timed out ')
				break	
			
			if (val['TOPIC'] == "alive"):
				temp_dk[val['IP']+":"+str(val['PROCESS_ID'])] = "alive"
			elif (val['TOPIC'] == "success"):
				my_mutex_stream.acquire()
				available_stream_table[val["IP"]+":"+str(val["PROCESS_ID"])]= "available" 
				my_mutex_stream.release()
				if (val['TYPE'] == "download"):
					print("Downloading done\n")

				elif (val['TYPE'] == "upload"):
					my_mutex_lookup.acquire()
					ob = value(val['USER_ID'], [val['IP']+":"+datakeeperFirstPort(val['IP'],val['PROCESS_ID'],alive_table)], [val['FILE_NAME']])
					lookup_table[val['FILE_NAME']] = ob
					my_mutex_lookup.release()
					print("Uploading done\n")
					#TODO:
					#You have to deal with the replica 
				# printAvailableStream(my_id,available_stream_table)
				# printLookup(my_id,lookup_table)
			else:
				print("Alive process got unexcpected topic\n")

		my_mutex_alive.acquire()
		for k, v in temp_dk.items():
			alive_table[k] = v
		my_mutex_alive.release()
		#printAlive(my_id,alive_table)
		time.sleep(1)		