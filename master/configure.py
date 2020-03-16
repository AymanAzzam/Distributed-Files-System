import multiprocessing

def configure(alive_table,available_stream_table,ports_list):
	f = open("config.txt", "r")
	replica_factor = int(f.readline())
	replica_period = int(f.readline())
	keepers_num = int(f.readline())
	processes_num = int(f.readline())

	for i in range(0,keepers_num):
		ip = f.readline().rstrip()			#.rstrip to erase "\n" from the ip end
		ip_port = int(f.readline())
		alive_table[ip+":"+str(ip_port)] = "dead"
		for j in range(0,processes_num):
			available_stream_table[ip+":"+str(ip_port+2*j)] = "available"
			#available_publish_table[ip+":"+str(ip_port+2*j+1)] = "available"
			ports_list.append(ip+":"+str(ip_port+2*j))
	return replica_factor, replica_period, keepers_num, processes_num