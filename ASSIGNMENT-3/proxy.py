import ast
import os
import socket
import sys
import time
 
#Setting the proxy host as our local host.
#The followin specifications are of the socket that is used to connect to our DNS Server.
UDP_IP = "127.0.0.1"
UDP_PORT = 5005 

#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

#Bind our socket to port 5004 to listen from DNS Server and get responses.
sock.bind(('127.0.0.1', 5004))

#Printing the results from the response received/ stored from the DNS Server.
def print_result(lis, name):
	print "\n" + name
	print "Non-authoritative answer"
	print name + "\t" + "canonical name = " + lis[0]["name"]
	for answer in lis:
		print "Name:\t" + answer["name"]
		print "Address:\t" + answer["address"]

#The list which stores the proxy cache in separate dictionaries.
cache = []

'''
Cache structure:
[{query, ID, TTL, Time, RESPONSE } ... ]
'''

'''
DNS Server respnse:
[ ID, TTL, Message]

Specific entries that were parsed from the response header in the previous assignment were sent as a message to the proxy server.
A basic python list with no packing can be used since we need not store everything as bytes.
The informtion can only be sent as a string over the sockets,
However the library AST is used to parse a string into lists and dictionaries.
Therefore we get our information.
'''

#The query to be looked up is taken as a raw string.
#Multiple queries need to be made when using a proxy server.
ns = raw_input("\nnslookup ")

'''
The main function of the cache is to check if the query is present in the cache. 
If it is it checks whether the query has timed out.
If it hasn't then the response is taken directly from the cache.
If it has, then the entry is deleted and a new entry is retrieved from the DNS Server.
If the query is not present in the cache, a request is sent to the DNS server with the hostname (port)
The response from the DNS server is recorded and sent back.
'''

while not ns == "exit":
	#splitting the query into host and port if required.
	if ':' in ns:
		ns.split(':')
		host = ns[0]
		port = ns[1]
	else:
		host = ns

	#found is used to check if a valid query is present in the cache.
	#valid query also includes upto date query (TTL not expired.)
	found = False
	for i in cache:
		if i["query"] ==  host:
			print "Query found in proxy:"
			#To check if the query is upto date
			if time.time() - i["time"] < i["ttl"]:
				print "Retrieving response from proxy"
				#We do not need to store a new entry in our cache yet.
				found = True
				#Print the result in the required format using the print_result function.
				print_result(i["response"], ns)
			#The time has exceeded the TTL, the particular entry needs to be removed from the cache.
			else:
				print "Exceeded time to live!"
				cache.remove(i)

	# A new or updated entry needs to be stored in the cache.
	if found == False:
		print "Sending request to DNS Name Server"
		sock.sendto(ns, (UDP_IP, UDP_PORT))
		inp = sock.recv(512)
		response = ast.literal_eval(inp)
		#Check if the response is valid.
		if response[0] == "Error":
			print "The query is not valid!"
		#If it is, create a dictionary to store the information.
		else:
			temp = {}
			temp["query"] = host
			temp["id"] = response[0]
			temp["ttl"] = response[1]
			temp["time"] = time.time()
			temp["response"] = response[2]
			cache.append(temp)
			#Print the response
			print_result(temp["response"], ns)

	#Wait for the next DNS query.
	ns = raw_input("\nnslookup ")
	