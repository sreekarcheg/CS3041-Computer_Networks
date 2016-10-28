"""
Ping server program to recieve client requests and send response packet back	
Tunable parameters, avg_delay and loss rate are incorporated to simulate real-time traffic
Run program under sudo user as: $python server.py x y
		(where 0<=x<=10)

"""

import socket   #for sockets
import sys  #for exit
import time
import math 
import datetime
import random
 

def createMessage(addr,port):  #msg generated: [0-2]: "UDP", [3-18]: destAddr, [19-22]: port, [23-48]: timestamp, [49-54]: platform, [55: ]: user message
    msg=''
    msg += "UDP"
    str_addr = str(addr)
    msg = msg + "0"*(16-len(str(addr))) + str(addr) + "0"*(4-len(str(port))) + str(port) + str(datetime.datetime.now()) + str(sys.platform) + "server message"
    return msg

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8886 # Arbitrary non-privileged port
 
# Datagram (udp) socket
loss_rate = int(sys.argv[1])

if(not(0<=loss_rate<=10)):
	print "First parameter should be between 0 to 10"
	exit(0)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print 'Socket created'
 
 
# Bind socket to local host and port

server.bind((HOST, PORT))

print 'Socket bind complete'
print 'Waiting for requests...'




packets_to_be_missed = []

while len(packets_to_be_missed)<loss_rate:
	x=random.randint(1,10)
	if x not in packets_to_be_missed:
		packets_to_be_missed.append(x)

sleepTime= float(sys.argv[2])
#now keep talking with the client
c=0
while 1:
	c += 1
	print ""
	print "Ping:", c
	data, addr = server.recvfrom(64)
	print 'Message recieved from client:', data
	if (c not in packets_to_be_missed):
		time.sleep(sleepTime) #Note: In Python, sleep only halts the execution of thread, not the execution of process
		msg=createMessage(addr, PORT)
		server.sendto(msg , addr)
		print 'Message sent to client:', msg
	
	
     
    
server.close()
