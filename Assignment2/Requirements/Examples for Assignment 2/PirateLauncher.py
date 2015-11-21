#!/usr/bin/python
# Copyright Notice: This code is based on material used by teaching staff of a previous COMP5416 course and must not be reposted.

import sys
from Tkinter import Tk
from Pirate import Pirate
import tkMessageBox

if __name__ == "__main__":
	try:
		fileName = sys.argv[1]	
	except:
		print "[Usage: python PirateLauncher.py Video_file]\n"
		exit()

	# Create a new client
	root = Tk()
	app = Pirate(root, fileName)
	app.master.title("Pirate GUI")
	root.mainloop()
