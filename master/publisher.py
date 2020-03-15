import zmq
import random
import sys
import time

port = "5556"


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:%s" % port)

while True:
	topic = random.randrange(9999,10005)
	messagedata = random.randrange(1,215) - 80
	print "%d %d" % (topic, messagedata)
	socket.send("bla: %d %d" % (topic, messagedata))
	time.sleep(1)