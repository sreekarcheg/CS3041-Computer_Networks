"""
HTTP server that accepts and parses a HTTP request, gets the requested file from the server's file system
creates an HTTP response message consisting of the requested file preceded by header lines and then sends 
the response directly to the client

If the requested file is not present in the server,the server sends a HTTP '404 Not Found' message
back to the client
"""

"""
Execution flow of the program:
    -Socket is created and binded to a port and the server is ready to service requests on that port
    -Server parses the messages it recieves and creats the response message and appends it appropriately to a HTTP header and sends the packet to the client
    -Server is prepared to service another message
"""

"""
Program is always garaunteed to exit gracefully, even when keyboard halt is entered
"""

import socket
import signal
import time

def generate_headers(code):   
    """
    Generate appropriate HTTP header in the form of a string depending on the response code
    """
    h = ''
    if (code == 200):
        h = 'HTTP/1.1 200 OK\n'
    elif(code == 404):
        h = 'HTTP/1.1 404 Not Found\n'
     

    current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) 
    h += 'Date: ' + current_date +'\n'
    h += 'Server: Simple-Python-HTTP-Server\n'
    h += 'Connection: close\n\n'  # signal that the conection wil be closed after complting the request

    return h



print ("Starting web server")
host =''
port = 8089

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print 'Socket create failed.\nError Code: ',msg[0], '\n Message: ', msg[1]

try:
    s.bind((HOST, PORT)) #I listen on this port.
    print 'Socket bind complete!'
except socket.error as msg:
    print 'Bind failed.\nError Code: ',msg[0], '\nMessage: ', msg[1]
    
print "Launched HTTP server on ", host, ":",port

while True:
    print ("\nAwaiting New connection")
    try:
        s.listen(10) #Can handle upto 10 clients.
    except socket.error as msg:
        print 'Listen failed.\nError Code: ',msg[0], '\nMessage: ', msg[1]

         
    conn, addr = server.accept()
         
    print("Got connection from:", addr)
         
    data = conn.recv(1024) #receive data from client
    string = bytes.decode(data) #decode it to string- for compatilbility issues
         
    #determine request method  (HEAD and GET are supported)
    request_method = string.split(' ')[0]
    print "Method: ", request_method
    print "Request body: ", string
         
         #if string[0:3] == 'GET':
    if (request_method == 'GET') or (request_method == 'HEAD') or (request_method == 'POST'):

        file_requested = string.split(' ')[1]

        file_requested = file_requested.split('?')[0]  # disregard anything after '?'
     
        if (file_requested == '/'):  # in case no file is specified by the browser
            file_requested = '/index.html' # load index.html by default
             

        file_requested = 'www' + file_requested
        print "Serving web page [",file_requested,"]"

        try:
            file_handler = open(file_requested,'rb')
            if (request_method == 'GET'):  #only read the file when GET
                response_content = file_handler.read() # read file content                       
            file_handler.close()

            response_headers = generate_headers(200)          
                 
        except Exception as e: #in case file was not found, generate 404 page
                print "File not found. Response code 404\n", e
                response_headers = generate_headers( 404)
             
                if (request_method == 'GET'):
                    response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"  
                 

        server_response =  response_headers.encode() # return headers for GET and HEAD
        if (request_method == 'GET'):
            server_response +=  response_content  # return additional conten for GET only


        conn.send(server_response)
        print "Closing connection with client"
        conn.close()

    else:
        print "Unknown HTTP request method:", request_method


