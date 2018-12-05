# -*- coding:utf-8 -*-

# The Laboratory AI
# revised for Masudayamon2018
# @Author Hideki Kano

import socket
import copy
import sys

# Settings
SERVER_IP = "localhost"
SERVER_PORT = 18420

#from classes.Action import Action
#from classes.GameState import GameState
#from classes.Worker import Worker

from classes.Message import Message
import solver

# raw message to Message class
def convertToMessage(raw_message):
    vector = raw_message.split()
    code = int(vector[0])
    instructions = vector[1:]
    return Message(code, instructions)

# argment check
if len(sys.argv) >= 3:
    ip = sys.argv[2]
else:
    ip = SERVER_IP
if len(sys.argv) >= 4:
    port = sys.argv[3]
else:
    port = SERVER_PORT

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port)) 
# main loop
while True:
    response_strings = client.recv(4096)
    # if message includes \n, execute respectly.
    for response_str in response_strings.decode().split('\n'):
        if not response_str:
            continue
        print("recv:", response_str)
        response_message = convertToMessage(response_str)
        reply_message = solver.solve(response_message)
        if reply_message is not None:
            print("send:" ,str(reply_message))
            client.send(str(reply_message).encode())













