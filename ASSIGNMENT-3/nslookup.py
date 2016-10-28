from random import randint
import os
import re
import socket
import struct
import sys

'''
Header Structure: RFC 1035

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
'''

def getHeader(response):
	'''
	The main information that we need from the header is the ancount
	This is stored in bytes 6-8
	'''
	temp = response[6:8]

	#Converting the response into int
	ret = int(str(temp).encode('hex'), 16)

def getBody(response, head):
	list_servers = []
	# parsing the response for x entries, specified by head
	pattern = re.compile(r"[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*")
	for res in head:
		string = str(res[4][0])
		if pattern.match(string):
			temp = {}
			temp["name"] = res[3]
			temp["address"] = res[4][0]
			list_servers.append(temp)

	return list_servers

def print_res(list_servers, website):
	'''
	Print the response from the body, which is stored in list_servers.
	'''
	print "Non-authoritative answer:"
	print website + "\tcanonical name = " + list_servers[0]["name"]
	for li in list_servers:
		print "Name:\t" + li["name"]
		print "Address:\t" + li["address"]

def getRequest(website):
	'''Make a DNS request.'''
	"""
	The flags in the 2nd row of the RFC header are as follows:
	QR -> 0
	OPcode -> 0000
	AA -> 0
	TC -> 0
	RD -> 1 (Recursion desired)
	RA -> 0 (Recursion availible)
	Z -> 0 (This should always be zero)
	RCODE -> 0000
	"""
	request = bytearray()

	#Header
	req_id = randint(0, 32768)
	temp = bytearray(struct.pack('L', req_id))	
	request += temp[:2][::-1]
	flags 	= int('0000000100000000', 2)
	temp = bytearray(struct.pack('L', flags))	
	request += temp[:2][::-1]
	qdcount = 1 
	temp = bytearray(struct.pack('L', qdcount))	
	request += temp[:2][::-1]
	ancount = 0
	temp = bytearray(struct.pack('L', ancount))	
	request += temp[:2][::-1] 
	nscount = 0 
	temp = bytearray(struct.pack('L', nscount))	
	request += temp[:2][::-1]
	arcount = 0 
	temp = bytearray(struct.pack('L', arcount))	
	request += temp[:2][::-1]
	
	#Creating the question the the required format
	#www.google.com -> 3www6google3com0
	url  = website.split('.')

	for sec in url:
		temp = bytearray(struct.pack('L', len(sec)))
		request += temp[:1][::-1]
		request += bytearray(sec)

	temp = 	bytearray(struct.pack('L', 0))
	request += temp[:1][::-1]
	#QType
	temp = 	bytearray(struct.pack('L', 1))
	request += temp[:2][::-1]
	#Qclass
	temp = 	bytearray(struct.pack('L', 1))
	request += temp[:2][::-1]

	return request

def nslookup(sock, website, ip):
	'''1. We perform the NSlookup in this function
	   2. In the latter half we parse the response
	'''

	#Connecting to the DNS Server.
	sock.connect((ip, 53))

	#Making the request in the proper format
	request = getRequest(website)

	#Sending the request through UDP socket
	try:
		sock.sendall(request)
	except:
		print "Message could not be sent"

	#receiving the response
	response = bytearray(sock.recv(512))
	head = socket.getaddrinfo(website,'www', 0,socket.SOCK_STREAM, 0, socket.AI_ADDRCONFIG | socket.AI_V4MAPPED | socket.AI_CANONNAME)
	
	#Parsing the response:
	header = getHeader(response)
	body = getBody(response, head)
	print_res(body, website)

#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

#Send the domain name(sys.argv[1]) and dns server for nslookup
nslookup(sock, sys.argv[1], '192.168.35.52')
