import os
import sys

attrib = [
    'MY_IP',
    'MASTER_IP',
    'MASTER_START_PORT',
    'DATA_KEEPER_IP',
    'DATA_KEEPER_START_PORT',
    'DATA_DIR',
    'CLIENT_IP',
    'CLIENT_START_PORT'
    ]

config = open('config.ini')

data = config.readlines()
print(data)
for i in range(len(data)):
    if(len(data[i])==1):
        continue
    end=data[i].find('=')
    print(data[i][0:end])
    print(data[i].find('='))
    print(data[i])