
def sendFile(file_name):
    f = open(file_name,"rb")
    message = {
        'DATA' : f.read(),
        'FILE_NAME' : file_name.split('/')[-1]
        }
    f.close()
    return message


def saveFile(video_data):
    f = open(video_data['FILE_NAME'],"wb")
    f.write(video_data['DATA'])
    f.close()