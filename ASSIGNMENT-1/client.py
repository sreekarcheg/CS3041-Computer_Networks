"""
A ping client program that uses a UDP socket. 
-Sends one packet every second and waits for one second to recieve a packet back
-In case of errors, appropriate handling is done to ensure the program doesn't crash
-After 10 packets are sent, the program prints the aggregate statistics of the trip times of the packets recieved

Program execution flow:

    ping(host)
        -doOnePing
            -sendOnePing
            -recieveOnePing
                -createMessage
    printStats
"""


import socket   #for sockets
import sys  #for exit
import time
import math 
import datetime
import select

host = 'localhost'
port = 8886



def doOnePing(host, timeout):
    """
    1. Creates a socket
    2. Calls the handler for sending packet(sendOnePing)
    3. Calls the handler for recieving packet with the tunable parameter timeout
    4. returns the RTT

    """
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sendOnePing(mySocket, host, timeout)
    #print "ping sent"
    try:
        delay = recieveOnePing(mySocket, host, timeout)
    except socket.gaierror, e:
        print "Failed. Socket error: '%s'"%(e[1])
    #print "packet recieved"
    if delay == None:
        print "Request timed out"
        missedPackets += 1
    mySocket.close()
    return delay


def sendOnePing(mySocket, host, timeout):
    """Calls the function to create message and then sends it"""
    global msg
    msg=createMessage(host,port)
    try:
        mySocket.sendto(msg,(host,port))

    except socket.error, (errno, msg):
        if errno == 1:
            # Operation not permitted
            msg = msg + "Process needs to be run as root "
            
            raise socket.error(msg)
        raise # raise the original error
 

    

def createMessage(host,port):  #msg generated: [0-2]: "UDP", [3-18]: destAddr, [19-22]: port, [23-48]: timestamp, [49-54]: platform, [55: ]: user message
    """Creates a message to be sent to the host in the format:
           [0-2]: "UDP", [3-18]: destAddr, [19-22]: port, [23-48]: timestamp, [49-54]: platform, [55: ]: user message 
    """
    msg=''
    msg += "UDP"
    str_port = str(port)
    msg = msg + "0"*(16-len(str(host))) + str(host) + "0"*(4-len(str_port)) + str_port + str(datetime.datetime.now()) + str(sys.platform) + "user message"
    return msg

def recieveOnePing(mySocket, host, timeout):
    """1. Recieve a packet and unpack the message content and the address
       2. Return the RTT 
    """

   
    startedSelect = time.time()
    whatReady = select.select([mySocket], [], [], 1)
    howLongInSelect = (time.time() - startedSelect) 
    if whatReady[0] == []: # Timeout
        mySocket.close()
        return 2
    
    try:
        recPacket, addr = mySocket.recvfrom(64)
        timeRecieved=float(str(datetime.datetime.now())[17:])
        timeSent=float(msg[40:49])
        # print "timeSent:", timeSent
        # print "timeRecieved:",timeRecieved
            
        
        if timeRecieved - timeSent >= 1:
            return 2
            
        else:
            return  timeRecieved - timeSent
    except:
        mySocket.close()
        return 2
    
    
def printStats():
    """
    Handles the printing of the aggregate statistics
    """

    print "---------statistics-----------" 
    global maxRTT; global minRTT;
    
    global totalTime
    global receivedPackets
    global missedPackets
    total = receivedPackets + missedPackets
    print "Missed packets:", missedPackets
    lossRate = float(missedPackets)/10
    if not maxRTT is None:
        maxRTT *= 1000
        minRTT *= 1000
        x = 0
        for i in range(len(delays)):
            x = x+(delays[i]*1000)
 
        average = x/len(delays)
        c = 0.0

        for i in range(len(delays)):
            c += math.pow(((delays[i]*1000)-average),2)
        c=math.sqrt(c/len(delays))

  
        print "min=%.4fms, max= %.4fms, average= %.4fms, stddev= %.4fms"%(minRTT, maxRTT, average,c) 
    print "%d packets sent, %d packets received, %.1f%% packet loss"%(total, receivedPackets, lossRate)

        
    
        

def ping(host, timeout = 1):

    """
    Main program. Send ten packets with a gap of 1 second between each. Print results for each packet sent. 
    If packet is recieved print the RTT. If not, print the timeout message. 
    Update maxRTT and minRTT


    """
    global maxRTT
    global minRTT
    global totalTime
    global receivedPackets
    global missedPackets

    global delays
    global begintime
    totalPackets=0

    while 1 :
        totalPackets += 1
        delay = doOnePing(host, timeout)
        


        if(delay*1000<=timeout):
            print "64 bytes from %s: id_seq=%d ttl=%d time=%.5fms"%(host,totalPackets, 64, delay*1000)
            delays.append(delay)
        else:
            print "Request timed out"
        
            
        if delay*1000 >= timeout:
            missedPackets += 1
        else:
            if maxRTT is None or delay > maxRTT:
                maxRTT = delay
            if minRTT is None or delay < minRTT:
                minRTT = delay
            totalTime += delay
            receivedPackets += 1

        time.sleep(1)# one second
        if totalPackets==10:
            printStats()
            return
    
    return delay


delays = []
maxRTT = None
minRTT = None
receivedPackets = 0
missedPackets = 0
totalTime = 0
beginTime=time.time()

ping(host)


