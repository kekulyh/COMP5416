# Copyright Notice: This code is based on material used by teaching staff of a previous COMP5416 course and must not be reposted.

from Tkinter import *
import tkMessageBox
import socket, threading, sys, traceback, os

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initialisation
	def __init__(self, master, serveraddr, serverport, udpport):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.udpPort = int(udpport)
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupPirate
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playPirate
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pausePirate
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2) 
	
	def setupPirate(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendTcpRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		self.sendTcpRequest(self.TEARDOWN)		
		self.master.destroy() # Close the gui window

	def pausePirate(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendTcpRequest(self.PAUSE)
	
	def playPirate(self):
		"""Play button handler."""
		if self.state == self.READY:
			# Create a new thread to listen for UDP packets
			threading.Thread(target=self.listenUdp).start()
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.sendTcpRequest(self.PLAY)
	
	def listenUdp(self):		
		"""Listen for UDP packets."""
		while True:
			try:
				data = self.udpSocket.recv(20480)
				print data
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
				
				# Upon receiving ACK for TEARDOWN request,
				# close the UDP socket
				if self.teardownAcked == 1:
                                        try:
                                                self.udpSocket.shutdown(socket.SHUT_RDWR)
                                        except:
                                                pass
					self.udpSocket.close()
					break
	
	def connectToServer(self):
		"""Connect to the Server. Start a new TCP session."""
		self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.tcpSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkMessageBox.showwarning('Oops!', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendTcpRequest(self, requestCode):
		"""Send TCP request to the server."""
		
		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target=self.recvTcpReply).start()			
			# Write the request to be sent.
			request = 'SETUP'
			
			# Keep track of the sent request.
			self.requestSent = self.SETUP
		
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Write the TCP request to be sent.
			request = 'PLAY'
			
			# Keep track of the sent request.
			self.requestSent = self.PLAY
		
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Write the TCP request to be sent.
			request = 'PAUSE'
			
			# Keep track of the sent request.
			self.requestSent = self.PAUSE
			
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:			
			# Write the TCP request to be sent.
			request = 'TEARDOWN'
			
			# Keep track of the sent request.
			self.requestSent = self.TEARDOWN
		else:
			return
		
		# Send the TCP request using tcpSocket.
		self.tcpSocket.send(request)
		
		print '\nData sent:\n' + request
	
	def recvTcpReply(self):
		"""Receive TCP reply from the server."""
		while True:
			reply = self.tcpSocket.recv(1024)
			
			if reply: 
				self.parseTcpReply(reply)
			
			# Close the TCP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				self.tcpSocket.shutdown(socket.SHUT_RDWR)
				self.tcpSocket.close()
				break
	
	def parseTcpReply(self, data):
		"""Parse the TCP reply from the server."""
		if int(data) == 200: 
			if self.requestSent == self.SETUP:
				# Update TCP state.
				self.state = self.READY
				
				# Open UDP port.
				self.openUdpPort() 
			elif self.requestSent == self.PLAY:
				self.state = self.PLAYING
			elif self.requestSent == self.PAUSE:
				self.state = self.READY
				
				# The play thread exits. A new thread is created on resume.
				self.playEvent.set()
			elif self.requestSent == self.TEARDOWN:
				self.state = self.INIT
				
				# Flag the teardownAcked to close the socket.
				self.teardownAcked = 1
		else:
			print "Oh no! A bad status code has been received!"
	
	def openUdpPort(self):
		"""Open UDP socket binded to a specified port."""
		
		# Create a new datagram socket to receive UDP packets from the server
		self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 2 seconds
		self.udpSocket.settimeout(2)
		
		try:
			# Bind the socket to the address using the UDP port given by the client user
			self.udpSocket.bind(('', self.udpPort))
		except:
			tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.udpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pausePirate()
		if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playPirate()
