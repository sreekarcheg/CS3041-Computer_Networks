#A simple HTTP server in Python
Developed a HTTP server that handles one HTTP request at a time. The web server accepts and parses the HTTP request from the server’s file system, generates a HTTP response message consisting of the requested file preceded by header lines, and then sends response directly to the client. If the requested file is not present in the server, the server sends a HTTP "404 Not Found" message back to the client.

##Abstract of implementation
A TCP socket is created and the socket is bound to the localhost
and a port not in current use. This simulates a server. The server then awaits for HTTP requests. It deals with each HTTP request accordingly. If the HTTP request is a GET request, the server fetches the file requested and then appends it to the HTTP headers indicating that response code of ‘OK 200’ and sends the packet.


##Screenshots
![ScreenShot 1](https://github.com/sreekarcheg/CS3041-Computer_Networks/blob/master/ASSIGNMENT-2/ScreenShot1.png)
![ScreenShot 2](https://github.com/sreekarcheg/CS3041-Computer_Networks/blob/master/ASSIGNMENT-2/ScreenShot2.png)

##Implementation details
- TCP socket is created and bound to localhost and port -Server listens for requests

- On request, server parses the request packet. If the packet is a GET or POST packet, the file(if present on server) is fetched and the contents of the file are appended to HTTP header and sent to client

- Wrapper handles for all possible errors have been implemented to guarantee graceful termination of the program under all circumstances

If the requested file does not exist on the server, the appropriate HTTP message with the error code 404 is generated and sent to the client.

Run server as: $python server.py
Run client as: $python Assgn02-client.py www.cse.iitk.ac.in 80 /users/dheeraj/cs425//index.html
