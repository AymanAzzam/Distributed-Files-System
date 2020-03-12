
def printLookup(proc_num,lookup_table):
	print("i am process number : %i inside print"  %proc_num)
	for k, v in lookup_table.items():
		print(k)
		lookup_table[k].valPrint()

def printAvailableStream(proc_num,available_stream_table):
	print("i am process number : %i inside print Available Stream"  %proc_num)
	for k, v in available_stream_table.items():
		print(k, v)	

def printAvailablePublish(proc_num,available_publish_table):
	print("i am process number : %i inside print Available Publish"  %proc_num)
	for k, v in available_publish_table.items():
		print(k, v)	