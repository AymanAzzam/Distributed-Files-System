def start_index_for_ip(ip,ports_list):
	index = 0
	while(ip != ports_list[index].split(":")[0]):
		index = index + 1
	return index