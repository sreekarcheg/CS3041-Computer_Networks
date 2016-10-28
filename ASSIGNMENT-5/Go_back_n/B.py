import time
import socket
import sys
from select import select
from thread import start_new_thread
import random
import struct

serverName = ''
serverPort = 8000

loss_index = 0
corrupted_index = 0

"""
After every 10 packets received, it selects random numbers from 0 to 9. 
The number of random numbers chosen are based on the probability of loss and corruption.
This is used to decide which packets are to be lost and whihc to be corrupted.
"""
def get_damage(num):
	rand = []
	for j in range(0,num):
		x = random.randint(0,9)
		while x in rand:
			x = random.randint(0,9)
		rand.append(x)
	return rand

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

"""
Function that initializes the socket.
"""
def B_init():
	try:
		socketB = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except :
		print 'Failed to create socket.'
		sys.exit()
	try:
		socketB.bind((serverName, serverPort))
		print 'Socket bind complete!'
	except:
		print 'Bind failed.'
		sys.exit(-1)
	return socketB

"""
This function takes the correct ordered and Uncorrupted message from layer 3 to layer 5.
"""
def tolayer5(message):
	print "Message Recieved in Application layer.\nMessage contents: " + message

"""
This funciton unpacks the header from the data receives usig struct unpack
It also stimulates packet corruption by using the damaged index to see which packets to send an incorrect header for.
"""
def getHeader(inputHead):
	global corrupted_index
	global corrupted_list
	header = struct.unpack('HHHH', inputHead)
	if corrupted_index == 0:
		corrupted_list = get_damage(corrupt_prob)
		if trace!= 0:
			print ("New corrupted list: ", corrupted_list)

	#if packet corrupted send incorrect header attributes
	if corrupted_index in corrupted_list:
		corrupted_index = (corrupted_index + 1) % 10
		return 99, 99, 99
	else:
		corrupted_index = (corrupted_index + 1) % 10
		return header[0], header[1], header[2]

"""
Recieve input from sender.
Separate the header and message
If the checksum matches proceed else send previous ack number
Check for ack number. If the expected and received acknum is same proceed else send the previous ack number back to the receiver.
Change the ack number
Send the message to layer5 (application layer).
"""
def B_input(socketB, packet, address):
	global ack_check

	acknum, seqnum, check = getHeader(packet[0:8])
	message = packet[8:28]
	
	temp = struct.pack('HHHH', seqnum, acknum, 0, 0)
	check_temp = temp + packet[8:28]

	if check == checksum(check_temp):
		if trace != 0:
			print "Uncorrupted packet received."
		if acknum == ack_check + 1:
			if trace != 0: 
				print "Packet " + str(seqnum) + " received"
				print "Sending packet to application layer"
			tolayer5(message)
			ack_check = ack_check + 1
			reply = "ack" + str(ack_check)
		else:
			if trace != 0:
				print "acknum did not match."
			reply = "ack" + str(ack_check)
	else:
		if trace != 0:
			print "Checksum did not match, packet corrupted"
		reply = "ack" + str(ack_check)
	try:
		socketB.sendto(reply, address)
		if trace != 0:
			print "ACK" + str(ack_check) + " sent to A."
	except:
		if trace != 0:
			"Failed to send response: '"+ reply + "' back to A."

# Initialize socket
socketB = B_init()

# loss probabilty
f1 = float(sys.argv[1])
loss_prob = int(f1*10)
print loss_prob

# corruption probabilty
f2 = float(sys.argv[2])
corrupt_prob = int(f2*10)
print corrupt_prob

trace = int(sys.argv[3])

#initialize ack_check.
ack_check = -1


"""
Keep receiving packets while true
"""
while True:
	packet, address = socketB.recvfrom(512)
	"""
	stimulate packet loss
	"""
	if loss_index == 0:
		loss_list = get_damage(loss_prob)
		if trace != 0:
			print ("New loss list: ", loss_list)

	if loss_index not in loss_list:
		if trace != 0:
			print "\nReceived message from A. " + packet[8:28] 
		B_input(socketB, packet, address)
	else:
		if trace != 0:
			print "\n Packet loss implemented."

	print "here"
	loss_index = (loss_index + 1) % 10