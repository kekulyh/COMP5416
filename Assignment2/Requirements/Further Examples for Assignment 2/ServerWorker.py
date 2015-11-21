# Copyright Notice: This code is based on material used by teaching staff of a previous COMP5416 course and must not be reposted.
# Note that the UDP port number is fixed at 2000 in this class.

from random import randint
import sys, traceback, threading, socket

class ServerWorker:
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'
	
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	clientInfo = {}
	
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo
		
	def run(self):
		threading.Thread(target=self.recvTcpRequest).start()
	
	def recvTcpRequest(self):
		"""Receive TCP request from the client."""
		connSocket = self.clientInfo['tcpSocket'][0]
		while True:            
			data = connSocket.recv(256)
			if data:
				print "Data received:\n" + data
				self.processTcpRequest(data)
	
	def processTcpRequest(self, data):
		"""Process TCP request sent from the client."""
		
		# Process SETUP request
		if data == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print "processing SETUP\n"
				self.state = self.READY
				
				# Send TCP reply
				self.replyTcp("200")
				
				# Get the UDP port from the last line
				self.clientInfo['udpPort'] = '2000' # Assume that the UDP port number is 2000
		
		# Process PLAY request 		
		elif data == self.PLAY:
			if self.state == self.READY:
				print "processing PLAY\n"
				self.state = self.PLAYING
				
				# Create a new socket for UDP
				self.clientInfo["udpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
				self.replyTcp("200")
				
				# Create a new thread and start sending UDP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendUdp)
				self.clientInfo['worker'].start()
		
		# Process PAUSE request
		elif data == self.PAUSE:
			if self.state == self.PLAYING:
				print "processing PAUSE\n"
				self.state = self.READY
				
				self.clientInfo['event'].set()
			
				self.replyTcp("200")

				self.clientInfo['udpSocket'].close() # Added line to prevent ghost sockets
		
		# Process TEARDOWN request
		elif data == self.TEARDOWN:
			print "processing TEARDOWN\n"
			flag = 1

                        try:
                                self.clientInfo['event'].set()
                        except:
                                print 'Attention! No playback thread was created before teardown!'
                                flag = 0
			
			self.replyTcp("200")
			
			# Close the UDP socket
			if flag == 1:
                                self.clientInfo['udpSocket'].close()
			
	def sendUdp(self):
		"""Send messages over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05) 
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet(): 
				break 
				
			data = randint(0, 65536)
			if data:
				try:
					address = self.clientInfo['tcpSocket'][1][0]
					port = int(self.clientInfo['udpPort'])
					self.clientInfo['udpSocket'].sendto(str(data),(address,port))
				except:
					print "UDP Connection Error"
		
	def replyTcp(self, code):
		"""Send reply over TCP to the client."""
		if code == '200':
			reply = '200'
			connSocket = self.clientInfo['tcpSocket'][0]
			connSocket.send(reply)
		
		# Error messages
		else:
			print "Oops! Bad status code"
