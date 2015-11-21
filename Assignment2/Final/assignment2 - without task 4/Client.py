"""
	File name: Client.py
	Author: Yahong Liu
	Version: 3.0
	Date: 17/10/2015
	Description: COMP5416 Assignment2 Video Streaming Client program
"""

from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os, time, json
from RtpPacket import RtpPacket

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
	def __init__(self, master, serverAddr, serverPort, rtpPort, fileName):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.pauseEvent = threading.Event()
		self.pauseEvent.set()
		self.quitEvent = threading.Event()
		self.quitEvent.clear()

		self.serverAddr = serverAddr
		self.serverPort = int(serverPort)
		self.rtpPort = int(rtpPort)
		self.fileName = fileName
		
		self.rtspVersion = "RTSP/1.0"
		self.CSeq = 0
		self.transportProtocol = "RTP/UDP"
		self.session = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.rtspConnect()
		self.frame = 0

	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "SETUP"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)

		# Create Play button
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "PLAY"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)

		# Create Puase button
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "PAUSE"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)

		# Create Teardown button
		self.terminate = Button(self.master, width=20, padx=3, pady=3)
		self.terminate["text"] = "TEARDOWN"
		self.terminate["command"] =  self.exitClient
		self.terminate.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=20)
		self.label.grid(row=0, column=0, columnspan=5, sticky=W+E+N+S, padx=5, pady=5) 


	"""SETUP function module"""
	def setupMovie(self):
		"""SETUP button handler."""
		if self.state == self.INIT:
			# send rtsp/tcp request to server
			self.sendSetupRtsp()

	def sendSetupRtsp(self):
		"""Send SETUP request over RTSP/TCP """
		# thread for listening rtsp/tcp reply
		self.rtspThread = threading.Thread(target=self.receiveRtspReply)
		self.rtspThread.start()
		self.CSeq += 1
		# create dict
		dictData = {}
		dictData['action'] = "SETUP"
		dictData['fileName'] = self.fileName
		dictData['rtspVersion'] = self.rtspVersion
		dictData['CSeq'] = self.CSeq
		dictData['transportProtocol'] = self.transportProtocol
		dictData['rtpPort'] = self.rtpPort
		# dict to JSON
		dictDataJSON = json.dumps(dictData)
		# track sent state
		self.requestSent = self.SETUP
		# send JSON to server
		self.rtspSocket.send(dictDataJSON)
		# print
		print dictData['action'] + " " + dictData['fileName'] + " " + dictData['rtspVersion'] + "\nCSeq: " + str(dictData['CSeq']) + "\nTransport: " + dictData['transportProtocol'] + "; client_port= " + str(dictData['rtpPort']) + "\n"


	"""PLAY function module"""
	def playMovie(self):
		"""PLAY button handler."""
		if self.state == self.INIT:
			if self.pauseEvent.isSet():
				tkMessageBox.showerror("Play", "Movie has not been setup, please setup movie first.")
		elif self.state == self.READY:
			if self.pauseEvent.isSet() == True:
				#if self.frame == 0:
				if tkMessageBox.askokcancel("Play", "Click OK to continue."):
					self.pauseEvent.clear()
					
					threading.Thread(target=self.listenRtp).start()
					
					self.sendPlayRtsp()

	def sendPlayRtsp(self):
		"""Send PLAY request over RTSP/TCP """
		self.CSeq += 1
		# create dict
		dictData = {}
		dictData['action'] = "PLAY"
		dictData['fileName'] = self.fileName
		dictData['rtspVersion'] = self.rtspVersion
		dictData['CSeq'] = self.CSeq
		dictData['session'] = self.session
		# dict to JSON
		dictDataJSON = json.dumps(dictData)
		# track sent state
		self.requestSent = self.PLAY
		# send JSON to server
		self.rtspSocket.send(dictDataJSON)
		# print
		print dictData['action'] + " " + dictData['fileName'] + " " + dictData['rtspVersion'] + "\nCSeq: " + str(dictData['CSeq']) + "\nSession: " + str(dictData['session']) + "\n"


	"""PAUSE function module"""
	def pauseMovie(self):
		"""PAUSE button handler."""
		if self.state == self.INIT:
			if self.pauseEvent.isSet():
				tkMessageBox.showerror("Pause", "Movie has not been setup, please setup movie first.")
		elif self.state == self.READY:
			if self.pauseEvent.isSet():
				tkMessageBox.showerror("Pause", "Movie is currently paused.")
		elif self.state == self.PLAYING:
			if self.pauseEvent.isSet() == False:
				self.pauseEvent.set()
				# send rtsp/tcp request to server 
				self.sendPauseRtsp()

	def sendPauseRtsp(self):
		"""Send PAUSE request over RTSP/TCP """
		self.CSeq += 1
		# create dict
		dictData = {}
		dictData['action'] = "PAUSE"
		dictData['fileName'] = self.fileName
		dictData['rtspVersion'] = self.rtspVersion
		dictData['CSeq'] = self.CSeq
		dictData['session'] = self.session
		# dict to JSON
		dictDataJSON = json.dumps(dictData)
		# track sent state
		self.requestSent = self.PAUSE
		# send JSON to server
		self.rtspSocket.send(dictDataJSON)
		# print
		print dictData['action'] + " " + dictData['fileName'] + " " + dictData['rtspVersion'] + "\nCSeq: " + str(dictData['CSeq']) + "\nSession: " + str(dictData['session']) + "\n"
		

	"""TEARDOWN function module"""
	def exitClient(self):
		"""TEARDOWN button handler."""
		flag = 0
		if self.pauseEvent.isSet():
			flag = 1
		else:
			self.pauseEvent.set() # Ensure video is not playing before the question is displayed
			self.sendPauseRtsp()
		if tkMessageBox.askokcancel("Exit", "Are you sure you want to quit?"):
		 	if self.pauseEvent.isSet() == False:
		 		self.pauseEvent.set() # Video playback needs to be stopped first
		 		self.quitEvent.set() # The other thread will clear this event variable just before it terminates
		 		self.quitEvent.wait() # Ensure that the thread responsible for reading the video file terminates first
			self.sendTeardownRtsp()
			self.master.destroy() # Close the GUI window
		elif flag == 0:
			self.pauseEvent.clear() # Allow playback to resume if video was playing beforehand
			self.sendPlayRtsp()
	
	def sendTeardownRtsp(self):
		"""Send TEARDOWN request over RTSP/TCP """
		self.CSeq += 1
		# create dict
		dictData = {}
		dictData['action'] = "TEARDOWN"
		dictData['fileName'] = self.fileName
		dictData['rtspVersion'] = self.rtspVersion
		dictData['CSeq'] = self.CSeq
		dictData['session'] = self.session
		# dict to JSON
		dictDataJSON = json.dumps(dictData)
		# track sent state
		self.requestSent = self.TEARDOWN
		# send JSON to server
		self.rtspSocket.send(dictDataJSON)
		# print
		print dictData['action'] + " " + dictData['fileName'] + " " + dictData['rtspVersion'] + "\nCSeq: " + str(dictData['CSeq']) + "\nSession: " + str(dictData['session']) + "\n"


	"""GUI exit handler"""
	def handler(self):
		self.exitClient()


	"""RTSP/TCP module"""
	def rtspConnect(self):
		"""Connect RTSP/TCP with server"""
		# create tcp socket
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print "Client RTSP/TCP socket created\n"
		try:
			# connect to tcp server
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
			print "Client RTSP/TCP socket connected\n"
		except:
			tkMessageBox.showerror('Connection Error', 'Connection error with server, please check your input server address and port.')
			exit()

	def receiveRtspReply(self):
		"""Receive the RTSP/TCP reply from server"""
		while True:
			receivedRtspDataJSON = self.rtspSocket.recv(1024)
			
			if receivedRtspDataJSON:
				self.processRtspReply(receivedRtspDataJSON)
			
			# Close the TCP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				"""Without try...except... will raise "error: [Errno 9] Bad file descriptor". Don't know why, seems like rtspSocket name is wrong."""
				try:
					self.rtspSocket.shutdown(socket.SHUT_RDWR)
				except:
					pass
				self.rtspSocket.close()
				break

	def processRtspReply(self,receivedRtspDataJSON):
		"""Process the RTSP/TCP reply"""
		receivedRtspData = json.loads(receivedRtspDataJSON)
		self.replyCode = receivedRtspData['replyCode']
		self.session = receivedRtspData['session']

		# when movie finishes, prepare for next time playing
		if receivedRtspData.has_key('finish'):
			time.sleep(1)
			self.state = self.INIT
			self.pauseEvent.set()
			self.frame = 0
			self.rtpSocket.close()
			self.rtpPort += 1

		# normal reply actions
		else:
			# Reply code is 200
			if self.replyCode == 200:
				
				if self.requestSent == self.SETUP:
					self.state = self.READY
					# connect rtp/udp socket
					self.rtpConnect()
				elif self.requestSent == self.PLAY:
					self.state = self.PLAYING
				elif self.requestSent == self.PAUSE:
					self.state = self.READY
					# The play thread exits. A new thread is created on resume.
					self.pauseEvent.set()
				elif self.requestSent == self.TEARDOWN:
					self.state = self.INIT
					# Flag the teardownAcked to close the socket.
					self.teardownAcked = 1
			# Reply code is 404
			elif self.replyCode == 404:
				print "404 FILE NOT FOUND"
			# Reply code is 500
			elif self.replyCode == 500:
				print "500 CONNECTION ERROR"


	"""RTP/UDP module"""
	def rtpConnect(self):
		"""Connect RTP/UDP with server"""
		# Create a new datagram socket to receive UDP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print "Client RTP/UDP socket created\n"
		# Set the timeout value of the socket to 2 seconds
		self.rtpSocket.settimeout(2)
		print "Client RTP/UDP socket timeout set\n"
		try:
			# Bind the socket to the address using the UDP port given by the client user
			self.rtpSocket.bind((self.serverAddr, self.rtpPort))
			print "Client RTP/UDP socket binded to PORT: %d\n" % self.rtpPort
		except:
			tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT: %d' % self.rtpPort)
			exit()
	
	def listenRtp(self):
		"""Listen for the RTP/UDP socket """
		while True:
			try:
				# read data over RTP/UDP socket
				receivedRtpData= self.rtpSocket.recv(20480)

				if receivedRtpData:
					# create RtpPacket instance
					rtpPacket = RtpPacket()
					# encode Rtppacket
					rtpPacket.decode(receivedRtpData)
					# RtpPacket FrameNbr
					self.rtpPacketFrame = rtpPacket.seqNum()
					if self.rtpPacketFrame > self.frame:
						self.frame = self.rtpPacketFrame
						#print "RtpPacket FrameNbr: " + str(self.rtpPacketFrame)
						print "Movie Frame: " + str(self.frame)
						self.updateScreen(self.frame, rtpPacket.getPayload())
					
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.pauseEvent.isSet(): 
					break
				# Upon receiving ACK for TEARDOWN request,
				# close the UDP socket
				if self.teardownAcked == 1:
					"""Without try...except... will raise "error: [Errno 9] Bad file descriptor". Don't know why, seems like rtspSocket name is wrong."""
					try:
						self.rtpSocket.shutdown(socket.SHUT_RDWR)
					except:
						pass
					self.rtpSocket.close()
					break


	"""Create local temp file, display it on GUI"""
	def updateScreen(self, frameNbr, payload):
		temp_file_name = str(frameNbr) + ".jpeg"
		file = open(temp_file_name, "wb")
		file.write(payload)
		file.close()
		time.sleep(0.035)
		photo = ImageTk.PhotoImage(Image.open(temp_file_name))
		self.label.configure(image = photo, height=288)
		self.label.image = photo
		os.remove(temp_file_name) # Comment out this line if you want the extracted JPEG images to remain on disk after playback finishes.