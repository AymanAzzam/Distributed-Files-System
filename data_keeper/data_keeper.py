import zmq
import cv2
import sys
import os


'''
Download:
    *Request: FILE_NAME
    *Response: FILE_NAME, FPS, FOURCC, WIDTH, HEIGHT, COUNT, #0, #1, ..., #[COUNT-1]

Upload:
    *Request: FILE_NAME, FPS, FOURCC, WIDTH, HEIGHT, COUNT, #0, #1, ..., #[COUNT-1]
'''
def sendFile(file_name, socket):
    videoData = cv2.VideoCapture('DATA/'+file_name)         #Capture Video
    fps = videoData.get(cv2.CAP_PROP_FPS)                   #GET FPS
    fourCC = int(videoData.get(cv2.CAP_PROP_FOURCC))        #GET FOURCC
    width = int(videoData.get(cv2.CAP_PROP_FRAME_WIDTH))    #GET WIDTH
    height = int(videoData.get(cv2.CAP_PROP_FRAME_HEIGHT))  #GET HEIGHT
    count = int(videoData.get(cv2.CAP_PROP_FRAME_COUNT))    #GET FRAMES COUNT

    message = {
        'FILE_NAME' : file_name,
        'FPS' : fps,
        'FOURCC' : fourCC,
        'WIDTH' : width,
        'HEIGHT' : height,
        'COUNT' : count
    }


    for i in range(count):
        msg.update({("#"+str(i)) : videoData.read()[1]})

    videoData.release()

    socket.send_pyobj(message)





def saveFile(video_data):
    file_name = video_data['FILE_NAME']
    fps = video_data['FPS']
    fourCC = video_data['FOURCC']
    width = video_data['WIDTH']
    height = video_data['HEIGHT']
    count = video_data['COUNT']

    out_video = cv2.VideoWriter('DATA/'+file_name, fourCC, fps,(width,height))

    for i in range(count):
        out_video.write(data[("#"+str(i))])
        out_video.release()





def processStream(message, socket):
    if ("PROCESS_TYPE") not in message:
        raise NameError("Error in streaming!")
    
    process = message['PROCESS_TYPE']

    if process == "Download":
    
        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")

        sendFile(message['FILE_NAME'],socket)
        
        '''
        #TODO
        Here notify the master with the successful download
        '''


    elif process == "Upload":
        
        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")

        if ("FPS") not in message:
            raise NameError("FPS is missed!")
        if ("FOURCC") not in message:
            raise NameError("FOURCC is missed!")
        if ("WIDTH") not in message:
            raise NameError("WIDTH is missed!")
        if ("HEIGHT") not in message:
            raise NameError("HEIGHT is missed!")
        if ("COUNT") not in message:
            raise NameError("COUNT is missed!")

        count = message['COUNT']

        for index in range(count):
            if ("#"+str(index)) not in message:
                raise NameError("frame #"+str(index)+" is missed!")
            
        saveFile(message)

        '''
        #TODO
        Here notify the master with the successful upload
        '''

    else:
        raise NameError("Error in streaming!")





def processReplicate(message, socket, context):
    if ("NODE_TYPE") not in message:
        raise NameError("Node type is missed!")

    
    if message['NODE_TYPE'] == "Source":

        if ("FILE_NAME") not in message:
            raise NameError("File name is missed!")
    
        if ("IP") not in message:
            raise NameError("IP is missed")

        if ("PORT") not in message:
            raise NameError("PORT is missed")
            
        temp_socket = context.socket(zmq.PAIR)
        temp_socket.connect("tcp://" + message['IP'] + ":" + message['PORT'])

        sendFile(message['FILE_NAME'],temp_socket)
        temp_socket.close()
        
        '''
        #TODO
        Here notify the master with the successful Sending in replication
        '''


    elif message['NODE_TYPE'] == "Destination":

        received_file = socket.recv_pyobj()
        saveFile(received_file['FILE_NAME'],received_file['FILE_CONTENT'])

        '''
        #TODO
        Here notify the master with the successful Receiving in replication
        '''
    else:
        raise NameError("Error in Node Type")





os.mkdir('DATA')

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
    [ONLY RUN ON THE FIRST NODE]
    Heart beats are sent here
    '''

    '''
    #TODO
    #When receiving Replicate notification
    processReplicate(message, stream, context)
    '''