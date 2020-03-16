
def printLookup(proc_num,lookup_table):
	print("i am process number : %i inside print Lockup table"  %proc_num)
	for k, v in lookup_table.items():
		print(k,v)

def printAvailableStream(proc_num,available_stream_table):
	print("i am process number : %i inside print Available Stream"  %proc_num)
	for k, v in available_stream_table.items():
		print(k, v)

def printAlive(proc_num,alive_table):
	print("i am process number : %i inside print Alive table"  %proc_num)
	for k, v in alive_table.items():
		print(k,v)
		# alive_table[k].valPrint()