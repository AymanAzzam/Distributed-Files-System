import multiprocessing
import sys
#import zmq


lookup_table= multiprocessing.Manager().dict()
print(type(lookup_table))

number_of_processes= 3

def updateLookup(proc_num,lookup, filename, value):
	print("i am process numberrr : %i"  %proc_num)
	lookup_table[filename]=value


def printLookup(proc_num,lookup):
	print("i am process number : %i inside print"  %proc_num)
	for k, v in lookup.items():
		print(k, v)





if __name__ == "__main__":
	with multiprocessing.Manager() as manager:
		#lookup_table= manager.dict()
		proc= {}
		'''
		for i in range(0,number_of_processes):
			proc[i]= multiprocessing.Process(target=updateLookup, args=(i,lookup_table))
			proc[i].start()
			proc[i].join()
			'''

		p1=	multiprocessing.Process(target=updateLookup, args=(1,lookup_table, "filename1","value1"))
		p1.start()
		p2=	multiprocessing.Process(target=printLookup, args=(2,lookup_table))
		p2.start()
		p3=	multiprocessing.Process(target=updateLookup, args=(3,lookup_table, "filename3","value3"))
		p3.start()
		p4=	multiprocessing.Process(target=printLookup, args=(4,lookup_table))
		p4.start()

		p1.join()
		p2.join()
		p3.join()
		p4.join()


		




