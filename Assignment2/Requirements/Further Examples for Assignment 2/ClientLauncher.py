# Copyright Notice: This code is based on material used by teaching staff of a previous COMP5416 course and must not be reposted.
# Note that the UDP port number must be set to 2000

import sys
from Tkinter import Tk
from Client import Client

if __name__ == "__main__":
	try:
		serverAddr = sys.argv[1]
		serverPort = sys.argv[2]
		udpPort = sys.argv[3]
	except:
		print "[Usage: ClientLauncher.py Server_name Server_port UDP_port]"
		exit()
	
	root = Tk()
	
	# Create a new client
	app = Client(root, serverAddr, serverPort, udpPort)
	app.master.title("Pirate")	
	root.mainloop()
