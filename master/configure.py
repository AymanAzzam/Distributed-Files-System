import multiprocessing

def configure():
	f = open("config.txt", "r")
	keepers_num = int(f.readline())
	processes_num = int(f.readline())

	available_stream_table = multiprocessing.Manager().dict()
	available_publish_table = multiprocessing.Manager().dict()
	ports_list = multiprocessing.Manager().list()

	for i in range(0,keepers_num):
		ip = f.readline().rstrip()			#.rstrip to erase "\n" from the ip end
		ip_port = int(f.readline())
		for j in range(0,processes_num):
			available_stream_table[ip+":"+str(ip_port+2*j)] = "available"
			available_publish_table[ip+":"+str(ip_port+2*j+1)] = "available"
			ports_list.append(ip+":"+str(ip_port+2*j))
	return keepers_num, processes_num,available_stream_table,available_publish_table,ports_list