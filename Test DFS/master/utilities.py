class value:
	#user_id = 5
	#datakeepers_list = []
	#paths_list = []
	def __init__(self, user_id, datakeepers_list, paths_list):
		self.user_id= user_id
		self.datakeepers_list= datakeepers_list
		self.paths_list= paths_list

	def valPrint(self):
		print(self.user_id, self.datakeepers_list, self.paths_list)

def start_index_for_ip(ip_port,process_num,ports_list):
	index = 0
	while(ip_port != ports_list[index]):
		index = index + process_num
	return index

def datakeeperFirstPort(ip,process_id,alive_table):
	out = 0
	for k,v in alive_table.items():
		if(k.split(":")[0] == ip and int(k.split(":")[1]) <= int(process_id)):
			out = max(int(k.split(":")[1]),out)
	return str(out)