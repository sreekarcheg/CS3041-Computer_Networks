#run as: python Assgn02-client.py www.cse.iitk.ac.in 80 /users/dheeraj/cs425//index.html
"""
Program that probes a HTML file and extracts the links in the file and downloads all the links in a local directory
"""
'''
Graceful termination of program is guaranteed. Successful execution is marked by printing 'Exiting...'to the terminal and
links are downloaded to the local directory
'''

import socket
import re
import sys
import os


os.environ['no_proxy'] = '127.0.0.1,localhost'
linkRegex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
CRLF = "\r\n\r\n"   #standard to mark header boundaries

def catch_links(filename):    #parse the html file and obtain the links pointed by it
    links = []
    html = open(filename, 'r')
    for line in html:
        if "href" in line:
            get = re.compile(r"\".*\"")
            link = get.search(line).group()
            link = link[1:-1]
            links.append(link)

    return links

def parse(html_filename):
    """
    For each link in the html file format it properly to get its correct path and pass it to GET function
    """
    L = catch_links(html_filename)
    for link in L:
        next_link = path + "/../" + str(link)
        #print next_link
        GET(host, port, next_link, link[2:])



def GET(server_host, server_port, file_path, write_file):
    """
    Get the html file and write it into a html file in the local directory

    1. Establish TCP connection with host
    2. Send a GET HTTP packet with appropriate headers
    3. Write the recieved packet into a file in the local directory by stripping the response HTTP header
    4. parse the main html file 
    """

    global count
    count += 1
    HOST = server_host   
    PORT = server_port                    
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   
    s.connect((HOST, PORT))
    path = file_path                     
    s.send("GET %s HTTP/1.0%s" % (path, CRLF))
    data = (s.recv(1000000))
    

    s.shutdown(1)
    s.close()

    filename = '/Users/hunter/Desktop/Mogi/' + write_file
    f = open(filename,'w')
    x=data.find('\r\n\r\n')
    f.write(data[x:])    #strip headers
    if count == 1:
        print "Main file read"
    f.close()
    if count==1:   #if condition to ensure that only the main html file is parsed, since function is part of mutual recursion. Also: To avoid infinite loop when a corrupt link is hit
        parse(filename)
        print "Links obtained"

count = 0   
host = str(sys.argv[1])
path = str(sys.argv[3])
port = int(sys.argv[2])

main_path = host + path

GET(host, port, path, "main.html")
print "Links successfully downloaded"
print "\nExiting..."

