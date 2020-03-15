import sys
import zmq

port = "5556"


# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, 'Child:')

print "Collecting updates from weather server..."
socket.connect("tcp://127.0.0.1:%s" % port)

while True:
	print ("waitig to recieve")
	print (socket.recv())

	#topic, messagedata = string.split()
	#print topic, messagedata


