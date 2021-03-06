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

from network.Message import Message
import network.solver as solver


# argment check
if len(sys.argv) >= 2:
    ip = sys.argv[1]
else:
    ip = SERVER_IP
if len(sys.argv) >= 3:
    port = int(sys.argv[2])
else:
    port = SERVER_PORT
if len(sys.argv) >= 4:
    mode = int(sys.argv[3])
else:
    mode = 0
print(ip,port)

flag = 0
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

        response_message = Message.createFromRawMessage(response_str)
        reply_message = solver.solve(response_message,mode)
        if reply_message is not None:
            print("send:" ,str(reply_message))
            client.send(str(reply_message).encode())
