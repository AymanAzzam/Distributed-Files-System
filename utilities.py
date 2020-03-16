import cv2

def sendFile(file_name):
    videoData = cv2.VideoCapture(file_name)         #Capture Video
    fps = videoData.get(cv2.CAP_PROP_FPS)                   #GET FPS (Frame per second)
    #fourCC = int(videoData.get(cv2.CAP_PROP_FOURCC))        #GET FOURCC (Enconding for some attributes)
    fourCC = cv2.VideoWriter_fourcc(*"mp4v")
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
        message.update({("#"+str(i)) : videoData.read()[1]})

    videoData.release()
    
    return message





def saveFile(video_data):
    file_name = video_data['FILE_NAME']
    fps = video_data['FPS']
    fourCC = video_data['FOURCC']
    width = video_data['WIDTH']
    height = video_data['HEIGHT']
    count = video_data['COUNT']
    
    
    out_video = cv2.VideoWriter(file_name, fourCC, fps,(width,height))

    for i in range(count):
        out_video.write(video_data[("#"+str(i))])

    out_video.release()