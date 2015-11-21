# Copyright Notice: This code is based on material used by teaching staff of a previous COMP5416 course and must not be reposted.
# Note that the UDP port number is fixed at 2000 in the ServerWorker class.

import sys, socket

from ServerWorker import ServerWorker

class Server:	
	
	def main(self):
		try:
			SERVER_PORT = int(sys.argv[1])
		except:
			print "[Usage: Server.py Server_port]"
			exit()
		TcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		TcpSocket.bind(('', SERVER_PORT))
		TcpSocket.listen(5)        

		# Receive client info (address,port) through TCP session
		while True:
			clientInfo = {}
			clientInfo['tcpSocket'] = TcpSocket.accept()
			ServerWorker(clientInfo).run()		

if __name__ == "__main__":
	(Server()).main()
