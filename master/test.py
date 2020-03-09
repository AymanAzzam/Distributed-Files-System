available_table = {}

f = open("config.txt", "r")
keepers_num = int(f.readline())
processes_num = int(f.readline())
for i in range(0,keepers_num):
	ip = f.readline().rstrip()
	ip_port = int(f.readline())
	for j in range(0,processes_num):
		available_table[ip+"/"+str(ip_port+j)] = True

print(available_table)