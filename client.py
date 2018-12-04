# -*- coding:utf-8 -*-

# The Laboratory AI
# revised for Masudayamon2018
# @Author Hideki Kano

import socket
import copy
import sys
import Queue

# Settings
SERVER_IP = "localhost"
SERVER_PORT = 18420
CLIENT_NAME = "Alice"
ALPHABETA_DEPTH = 8
ACTION_ID_LIST = [
    "1-1", 
    "2-1", "2-2", "2-3",
    "3-1", "3-2", "3-3",
    "4-1", "4-2", "4-3",
    "5-1", "5-2", "5-3",
    "6-1", "6-2"
]
SEASON_ID_LIST = ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b"]
KIND_ID_LIST = ["P", "A", "S"]

#from classes.Action import Action
#from classes.GameState import GameState
#from classes.Worker import Worker

from classes.Message import Message
from solver import solver

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
    for response_str in response_strings.split('\n'):
        if not response_str:
            continue
        print("recv:", response_str)
        response_message = convertToMessage(response_str)
        reply_message = solver.solve(response_message)
        if reply_message is not None:
            print("send:" ,str(reply_message))
            client.send(str(reply_message))













