import multiprocessing
from multiprocessing import Lock
import sys
#import zmq
import random
#import time
from master_client import *
from configure import *
from print_tables import *
from replica import *

ip1 = "127.0.0.1";	port = int(sys.argv[1]);	n = int(sys.argv[2])
keepers_num = 0;	processes_num = 0
replica_factor = 3

lookup_table = multiprocessing.Manager().dict()
alive_table = multiprocessing.Manager().dict()
available_stream_table = multiprocessing.Manager().dict()
available_publish_table = multiprocessing.Manager().dict()
ports_list = multiprocessing.Manager().list()

class value:
	def __init__(self, user_id, datakeepers_list, paths_list):
		self.user_id= user_id
		self.datakeepers_list= datakeepers_list
		self.paths_list= paths_list

	def valPrint(self):
		print(self.user_id, self.datakeepers_list, self.paths_list)

def updateLookup(proc_num,filename, value,lookup_table):
	print("i am process numberrr : %i"  %proc_num)
	lookup_table[filename]=value

if __name__ == "__main__":
	with multiprocessing.Manager() as manager:

		


		my_mutex = Lock()
		my_id = random.randrange(10000)

		replica_factor, replica_period, keepers_num, processes_num,alive_table,available_stream_table,available_publish_table,ports_list = configure()
		
		p = []
		for i in range(0,n):
			p.append(multiprocessing.Process(target=master_client, args=(alive_table,available_stream_table,ports_list,lookup_table,ip1,port,keepers_num,processes_num,my_mutex,)))
			p[i].start()
			port = port + 1

		# 1) check the replicas for all files
		p.append(multiprocessing(target=replica, args=(replica_factor,replica_period,alive_table,lookup_table,available_stream_table,ports_list,processes_num,my_mutex, )))
		p[n].start()
		# 2) recieve the heart beat
		p.append(multiprocessing(target=alive, args=(ip,port,alive_period, alive_table,available_stream_table,my_mutex,)))
		p[n+1].start()

		for i in range(0,n+2):
			p[i].join()