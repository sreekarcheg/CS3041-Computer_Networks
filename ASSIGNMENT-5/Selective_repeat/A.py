"""
A program to implement the selective repeat algorithm for reliable data transfer
The rdt version is 3.0

This section of the program implements the sender side of the rdt.
"""
import socket
import sys
from select import select
import struct

msg = {}

serverName = ''
serverPort = 8000

"""
The checksum calculates a sum from the given data and headers.
It is used to check if the data received is corrupted
"""
def checksum(source_string):
	sum = 0
	count_to = (len(source_string) / 2) * 2
	count = 0
	while count < count_to:
		this_val = ord(source_string[count + 1])*256+ord(source_string[count])
		sum = sum + this_val
		sum = sum & 0xffffffff 
		count = count + 2
	if count_to < len(source_string):
		sum = sum + ord(source_string[len(source_string) - 1])
		sum = sum & 0xffffffff 
	sum = (sum >> 16) + (sum & 0xffff)
	sum = sum + (sum >> 16)
	answer = ~sum
	answer = answer & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer

#The question statement requires a fixed data-length of 20 bytes. 
# This is to ensure uniformity
def get_Data(data):
	length = len(data)
	if length <= 20:
		string = "x" * (20 - length)
	else:
		print "Data too long, transmitting only 20 bytes."
		data = data[0:20]
		length = 20
	return length, data

"""
 The packet is made using a python struct.
 The field in the header are sequence number, Acknowlegment number, checksum, and data length
"""
def get_Packet(data, seqnum, acknum):
	header = struct.pack('HHHH', seqnum, acknum, 0, 0)
	length, payload = get_Data(str(data))
	my_checksum = checksum(header + payload)
	header = struct.pack('HHHH', seqnum, acknum, my_checksum, length)
	return header + payload

"""
Function that initializes the socket.
"""
def A_init():
	try:
		socketA = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print "Socket created"
	except:
		print "Socket creation failed"

		sys.exit()
	return socketA

"""
We check for the packet using a timeout. 
The timer stops as soon as the packet is received. And returns flase
If the timer rus out, it returns true
"""
def A_timerinterrupt(socketA, time):
	toReturn = select([socketA], [], [], time)
	if toReturn[0] == []:
		return True
	else:
		return False

"""
This function receives the acknowledgment from the sender and returns the ack number.
"""
def A_input(socketA):
	data, address = socketA.recvfrom(512)
	if trace != 0:
		print "Acknowlegment received: " + data
	if data[0:3] == "ack":
		ret = int(data[3])
	else:
		ret = -1
	return ret

"""
This function sends the packet over the network.
"""
def tolayer3(packet, socketA):
	socketA.sendto(packet, (serverName, serverPort))

"""
This function ensures that the next packet received by the server is in the correct order.
It takes into account both the ack number and timeout.
"""
def A_sendRecv(socketA, packet, seq, time_out):
	tolayer3(packet, socketA)

	lost = A_timerinterrupt(socketA, time_out)

	while lost == True:
		if trace != 0:
			print "Packet " + str(seq) + " timedOut. Resending packet..."
		tolayer3(packet, socketA)
		lost = A_timerinterrupt(socketA, 1)

	return A_input(socketA)

"""
This is the main function the packet is made and sent out.
The correct packet is marked as received.
This function calls onto all the other functions. 
"""
def A_output(socketA, message, acknum, time_out):
	
	msg["data"] = message

	packet = get_Packet(msg["data"], message, acknum)

	retAck = A_sendRecv(socketA, packet, message, time_out)

	while not retAck == acknum:
		if trace != 0:
			print "Packet " + str(message) + " lost. Resending packet..."
		retAck = A_sendRecv(socketA, packet, message, time_out)

	print str(message) + " Delivered! \n"


#initializing the UDP socekt.
socketA = A_init()
ack = 1
time_out = int(sys.argv[2])
trace = int(sys.argv[3])

#Sending the required number of packets one by one.
n = int(sys.argv[1])
for i in range (0, n):
	if ack == 0:
		ack = 1
	else:
		ack = 0
	A_output(socketA, i+1, ack, time_out)
