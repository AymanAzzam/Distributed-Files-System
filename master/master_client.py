from multiprocessing import Lock
import zmq
import random
from print_tables import *
from utilities import *

def master_client(alive_table,available_stream_table,ports_list,lookup_table,ip1,port1,keepers_num,processes_num,my_mutex):
	my_id = random.randrange(10000)
	starting_dk_port_index = random.randrange(keepers_num*processes_num)

	context = zmq.Context()
    
	client = context.socket(zmq.REP)            #REP because it needs to receive then send
	client.bind("tcp://%s:%i"%(ip1,port1))      #client will connect to this port

	while True:
		data = client.recv_pyobj()              #Receive message from client 
		
		#receiving dictionary contains command(upload/download) and file(file_Data for upload/file_name for download)
		print("master_client_id %i received command type %s\n" %(my_id, data['PROCESS']))

		if(data['PROCESS']=="upload"):
			my_mutex.acquire()
			print("Master searching about available port  to upload\n")
			while(available_stream_table[ports_list[starting_dk_port_index]] == "busy" or alive_table[ports_list[starting_dk_port_index].split(":")[0]] == "dead"):
				starting_dk_port_index=(starting_dk_port_index+1)%(keepers_num*processes_num)
			print("Master sent %s for client to upload to\n"%(ports_list[starting_dk_port_index]))
			available_stream_table[ports_list[starting_dk_port_index]] = "busy"
			my_mutex.release()
			msg={
				'IP' : ports_list[starting_dk_port_index].split(":")[0],
				'PORT' : ports_list[starting_dk_port_index].split(":")[1]
			}
			client.send_pyobj(msg)

		elif(data['PROCESS']=="download"):
			# filename may be invalid !!!!
			if(data['FILE_NAME'] not in lookup_table):
				msg = {'FILE_NAME':"File name invalid"}
				client.send_pyobj(msg)
				continue
			else:
				val = lookup_table[data['FILE_NAME']]
				
			datakeeper_list = val.datakeepers_list
			my_mutex.acquire()

			print("Master searching about available port  to download\n")
			ip_index_temp = start_index_for_ip(datakeeper_list[0].split(":")[0],ports_list);	ip_index = ip_index_temp
			#WARNING
			#There's a problem in the while loop => list index out of range 
			while(available_stream_table[ports_list[ip_index]] == "busy" or alive_table[ports_list[starting_dk_port_index].split(":")[0]] == "dead"):
				ip_index = (ip_index + 1) % (ip_index + processes_num)
			print("Master sent %s for client to download from\n"%(ports_list[starting_dk_port_index]))	
			available_stream_table[ports_list[ip_index]] = "busy"
			my_mutex.release()

			msg={
				'IP' : ports_list[ip_index].split(":")[0],
				'PORT' : ports_list[ip_index].split(":")[1]
			}
			client.send_pyobj(msg)
		else:
			print("master_client_id %i received invalid command\n" %(my_id))

		printAvailableStream(my_id,available_stream_table)