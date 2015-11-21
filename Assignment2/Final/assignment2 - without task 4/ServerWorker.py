"""
	File name: ServerWorker.py
	Author: Yahong Liu
	Version: 3.0
	Date: 17/10/2015
	Description: COMP5416 Assignment2 Video Streaming ServerWorker program
"""

import socket, threading, sys, traceback, os, time, json
from random import randint
from RtpPacket import RtpPacket
from VideoStream import VideoStream

import inspect
import ctypes 

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


	"""Initialization"""
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo
		print "ServerWorker init done\n"


	"""Create RTSP thread"""
	def run(self):
		self.rtspThread = threading.Thread(target=self.receiveRtsp)
		self.rtspThread.start()
		print "ServerWorker run done\n"



	"""RTSP/TCP module"""
	def receiveRtsp(self):
		"""connect rtsp/tcp socket"""
		rtspSocket = self.clientInfo['rtspSocket'][0]
		print "ServerWorker RTSP/TCP socket connected\n"
		while True:
			receivedRtspDataJSON = rtspSocket.recv(256)
			if receivedRtspDataJSON:
				self.processRtsp(receivedRtspDataJSON)

	def processRtsp(self,receivedRtspDataJSON):
		"""Handle received RTSP request"""
		# json tp dict
		receivedRtspData = json.loads(receivedRtspDataJSON)
		self.action = receivedRtspData['action']

		# SETUP module
		if self.action == self.SETUP and self.state == self.INIT:

			self.fileName = receivedRtspData['fileName']
			self.rtspVersion = receivedRtspData['rtspVersion']
			self.CSeq = receivedRtspData['CSeq']
			self.transportProtocol = receivedRtspData['transportProtocol']
			self.rtpPort = receivedRtspData['rtpPort']
			
			try:
				self.file = VideoStream(self.fileName)
				# create a session
				self.session = randint(0, 65536)
				# set frame number to 0
				self.frameNbr = 0
				# set rtpError to 0 
				self.rtpError = 0
				# change state on server
				self.state = self.READY
			except IOError:
				self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

			# send rtsp/tcp reply
			self.replyRtsp(200)

			print "ServerWorker SETUP"

		# PLAY module
		elif self.action == self.PLAY and self.state == self.READY:
			self.fileName = receivedRtspData['fileName']
			self.rtspVersion = receivedRtspData['rtspVersion']
			self.CSeq = receivedRtspData['CSeq']
			self.session = receivedRtspData['session']
			# change state on server
			self.state = self.PLAYING
			# connect RTP/UDP socket
			self.rtpScoket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.rtpThread = threading.Thread(target=self.rtpConnect)
			self.rtpThread.start()
			# send rtsp/tcp reply
			self.replyRtsp(200)

			print "ServerWorker PLAY"

		# PAUSE module
		elif self.action == self.PAUSE and self.state == self.PLAYING:
			self.fileName = receivedRtspData['fileName']
			self.rtspVersion = receivedRtspData['rtspVersion']
			self.CSeq = receivedRtspData['CSeq']
			self.session = receivedRtspData['session']
			# change state on server
			self.state = self.READY
			# stop playEvent
			self.playEvent.set()
			# send rtsp/tcp reply
			self.replyRtsp(200)
			# Added line to prevent ghost sockets
			self.rtpScoket.close()

			print "ServerWorker PAUSE"

		# TEARDOWN module
		elif self.action == self.TEARDOWN:
			self.fileName = receivedRtspData['fileName']
			self.rtspVersion = receivedRtspData['rtspVersion']
			self.CSeq = receivedRtspData['CSeq']
			self.session = receivedRtspData['session']
			# flag of RTP/UDP socket
			flag = 1
			try:
				# stop playEvent
				self.playEvent.set()
			except:
				flag = 0
				print 'Attention! No playback thread was created before teardown!'
			# send rtsp/tcp reply
			self.replyRtsp(200)
			# Close the RTP/UDP socket
			if flag == 1:
				self.rtpScoket.close()

			print "ServerWorker TEARDOWN"


	def replyRtsp(self, replyCode):
		"""Reply RTSP to client"""
		if replyCode == 200:
			# create dict
			dictReply = {}
			dictReply['rtspVersion'] = self.rtspVersion
			dictReply['replyCode'] = 200
			dictReply['replyAction'] = "OK"
			dictReply['CSeq'] = self.CSeq
			dictReply['session'] = self.session
			# dict to JSON
			dictReplyJSON = json.dumps(dictReply)
			# connect rtsp/tcp socket
			rtspSocket = self.clientInfo['rtspSocket'][0]
			# send JSON to clinet
			rtspSocket.send(dictReplyJSON)
			#print
			print dictReply['rtspVersion'] + " " + str(dictReply['replyCode']) + " " + dictReply['replyAction'] + "\nCSeq: " + str(dictReply['CSeq']) + "\nSession: " + str(dictReply['session']) +"\n"

		elif replyCode == 404:
			# create dict
			dictReply = {}
			dictReply['rtspVersion'] = self.rtspVersion
			dictReply['replyCode'] = 404
			dictReply['replyAction'] = "FILE NOT FOUND"
			dictReply['CSeq'] = self.CSeq
			dictReply['session'] = self.session
			# dict to JSON
			dictReplyJSON = json.dumps(dictReply)
			# connect rtsp/tcp socket
			rtspSocket = self.clientInfo['rtspSocket'][0]
			# send JSON to clinet
			rtspSocket.send(dictReplyJSON)
			#print
			print dictReply['rtspVersion'] + " " + str(dictReply['replyCode']) + " " + dictReply['replyAction'] + "\nCSeq: " + str(dictReply['CSeq']) + "\nSession: " + str(dictReply['session']) +"\n"

		elif replyCode == 500:
			# create dict
			dictReply = {}
			dictReply['rtspVersion'] = self.rtspVersion
			dictReply['replyCode'] = 500
			dictReply['replyAction'] = "CONNECTION ERROR"
			dictReply['CSeq'] = self.CSeq
			dictReply['session'] = self.session
			# dict to JSON
			dictReplyJSON = json.dumps(dictReply)
			# connect rtsp/tcp socket
			rtspSocket = self.clientInfo['rtspSocket'][0]
			# send JSON to clinet
			rtspSocket.send(dictReplyJSON)
			#print
			print dictReply['rtspVersion'] + " " + str(dictReply['replyCode']) + " " + dictReply['replyAction'] + "\nCSeq: " + str(dictReply['CSeq']) + "\nSession: " + str(dictReply['session']) +"\n"



	"""RTP/UDP module"""
	def rtpConnect(self):
		"""Send messages over UDP."""
		while True:
			# wait until current rtp has sent data
			self.playEvent.wait(0.05)
			# Stop sending if request is PAUSE or TEARDOWN
			if self.playEvent.isSet():
				break
			
			# RtpPacket arguments
			version = 2
			padding = 0
			extension = 0
			cc = 0
			seqnum = self.file.frameNbr()
			marker = 0
			pt = 26
			ssrc = 34

			payload = self.file.nextFrame()

			# if not finished playing
			if payload:	
				# create RtpPacket instance
				rtpPacket = RtpPacket()
				# encode Rtppacket
				rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
				# getPacket
				packet = rtpPacket.getPacket()
				# get the RTP/UDP address of client
				self.rtpAddress = self.clientInfo['rtspSocket'][1][0]
				try:
					self.rtpScoket.sendto(packet,(self.rtpAddress, self.rtpPort))
				except:
					self.rtpError += 1
					print "ServerWorker RTP/UDP Sending Error: %d" % self.rtpError
			
			# if finished playing, inform client
			else:
				self.state = self.INIT
				self.finishPlaying(seqnum-1)
				
				break

				"""Terminate thread. Problem with invalid thread id"""
				self._async_raise(self.rtpThread.ident, SystemExit)


	"""Finish playing function"""
	def finishPlaying(self, frameNbr):
		dictReply = {}
		dictReply['rtspVersion'] = self.rtspVersion
		dictReply['replyCode'] = 200
		dictReply['replyAction'] = "OK"
		dictReply['CSeq'] = self.CSeq
		dictReply['session'] = self.session
		dictReply['finish'] = frameNbr
		# dict to JSON
		dictReplyJSON = json.dumps(dictReply)
		# connect rtsp/tcp socket
		rtspSocket = self.clientInfo['rtspSocket'][0]
		# send JSON to clinet
		rtspSocket.send(dictReplyJSON)
		#print
		print dictReply['rtspVersion'] + " " + str(dictReply['replyCode']) + " " + dictReply['replyAction'] + "\nCSeq: " + str(dictReply['CSeq']) + "\nSession: " + str(dictReply['session']) +"\n" + "Finish Playing Frame Number: " + str(dictReply['finish'])


	"""Raise exception to terminate thread"""
	def _async_raise(self, tid, exctype):
		if not inspect.isclass(exctype):
			exctype = type(exctype)
		res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
		if res == 0:
			raise ValueError("invalid thread id")
		elif res != 1:
			# if it returns a number greater than one, you're in trouble, 
			# and you should call it again with exc=NULL to revert the effect
			ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
			raise SystemError("PyThreadState_SetAsyncExc failed")