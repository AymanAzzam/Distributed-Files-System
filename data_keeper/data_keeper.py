import zmq
import cv2

def sendFile(file_name, socket):
    pass

def saveFile(file_name, file_content):
    pass

def processStream(message, socket):
    if message.has_key("PROCESS_TYPE") == False:
        raise NameError("Error in streaming!")
    
    process = message['PROCESS_TYPE']

    if process == "Download":
    
        if message.has_key("FILE_NAME") == False:
            raise NameError("File name is missed!")

        sendFile(message['FILE_NAME'],socket)
        
        '''
        #TODO
        Here notify the master with the successful download
        '''


    elif process == "Upload":
        
        if message.has_key("FILE_NAME") == False:
            raise NameError("File name is missed!")

        if message.has_key("FILE_CONTENT") == False:
            raise NameError("File content is missed!")

        saveFile(message['FILE_NAME'],message['FILE_CONTENT'])

        '''
        #TODO
        Here notify the master with the successful upload
        '''

    else:
        raise NameError("Error in streaming!")


def processReplicate(message, socket, context):
    if message.has_key("NODE_TYPE") == False:
        raise NameError("Node type is missed!")

    
    if message['NODE_TYPE'] == "source":

        if message.has_key("FILE_NAME") == False:
            raise NameError("File name is missed!")
    
        if message.has_key("IP") == False:
            raise NameError("IP is missed")

        if message.has_key("PORT") == False:
            raise NameError("PORT is missed")
            
        temp_socket = context.socket(zmq.PAIR)
        temp_socket.connect("tcp://" + message['IP'] + ":" + message['PORT'])

        sendFile(message['FILE_NAME'],temp_socket)
        temp_socket.close()
        
        '''
        #TODO
        Here notify the master with the successful Sending in replication
        '''


    elif message['NODE_TYPE'] == "destination":

        received_file = socket.recv_pyobj()
        saveFile(received_file['FILE_NAME'],received_file['FILE_CONTENT'])

        '''
        #TODO
        Here notify the master with the successful Receiving in replication
        '''
    else:
        raise NameError("Error in Node Type")






stream_port = 5556
#publisher_port here
context = zmq.Context()

stream = context.socket(zmq.PAIR)
#publisher socket here

stream.bind("tcp://127.0.0.1:" + str(stream_port))
#publisher bind here


while True:
    try:
        message = stream.recv_pyobj(zmq.DOWNTWAIT)
        processStreammessage,stream)
    except zmq.Again:
        pass

    '''
    #TODO
    Heart beats are sent here
    '''

    '''
    #TODO
    #When receiving Replicate notification
    processReplicate(message, stream, context)
    '''