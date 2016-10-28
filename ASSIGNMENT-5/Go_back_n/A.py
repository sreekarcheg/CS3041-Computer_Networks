import socket
import sys
from select import select
import struct
import thread

msg = {}

received = ''

serverName = ''
serverPort = 8000

#The checksum calculates a sum from the given data and headers.
#It is used to check if the data received is corrupted
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
def get_Packet(data, seqnum):
	header = struct.pack('HHHH', seqnum, seqnum, 0, 0)
	length, payload = get_Data(str(data))
	my_checksum = checksum(header + payload)
	header = struct.pack('HHHH', seqnum, seqnum, my_checksum, length)

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
This checks for the acknowlegment number from the receiver.
If a packet has timed out the window is started from the packet, after the last acked packet.
If the acknowlegment received is correct, then the window_left is incremented by one. Indicating that there is an empty slot in the window.
The ack number is also incremented to point to the next expected ack.
If an Incorrect ack is recevied, the sender ignores it.
"""
def A_input(socketA, time_out):
	global  seq, acked, window_left

	toReturn = select([socketA], [], [], time_out)
	if toReturn[0] == []:
		if trace != 0:
			print "No Acknowlegment received! Packet timed out"
		seq = acked + 1
		window_left = 8
		i = seq
	 	
	else:
		data, address = socketA.recvfrom(512)
		if trace != 0:
			print "Acknowlegment received: " + data	
		if data[0:3] == "ack":
			if int(data[3:]) == acked + 1:
			 	print "\n Packet " + str(acked + 1) + " received!\n"
				acked += 1
				window_left += 1
			else:
				if trace != 0:
					print "Incorrect ack received for " + str(acked +1)
		else:
			if trace != 0:
				print "Data received is corrupted."
			seq = acked + 1
			window_left = 8
			i = seq

"""
This function sends the packet over the network.
"""
def tolayer3(packet, socketA):
	socketA.sendto(packet, (serverName, serverPort))

"""
The A_out function first sends all the packets and then starts waiting to receive acknowledgments parallely.
As long as there is a slot in he window and all the packets have not been sent, we can continur sending packets in the sequential order.
This function also calls functions to make the packets that have to be delivered to the receiver.
"""
def A_out(socketA, time_out, window_size, n):
	global i
	global seq 
	global acked
	global window_left
	i = 0
	seq = 0
	acked = -1
	window_left = window_size
	while acked < n-1:
		if (window_left > 0) and (seq < n):
			if trace != 0:
				print "Sending packet " + str(i)
			packet = get_Packet(i, seq) 
			try:
				tolayer3(packet, socketA)
				if trace != 0:
					print "sent to layer 3"
			except:
				print "failed to send data"
				exit(-1)
			window_left -= 1
			i += 1
			seq += 1
		if (window_left == 0) or (seq == n):
			if trace != 0:
				print "Waiting for Acknowlegment."
			A_input(socketA, time_out)

#initializing the UDP socekt.
socketA = A_init()
time_out = int(sys.argv[2])
trace = int(sys.argv[3])
window_size = 8

#Sending the required number of packets one by one.
n = int(sys.argv[1])

#Starting the go-back-n routing algorithm
A_out(socketA, time_out, window_size, n)