# Copyright Notice: This code is based on material used by teaching staff of a previous COMP5416 course and must not be reposted.

from Tkinter import *
import tkMessageBox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os, time

class Pirate:
	# Initialisation
	def __init__(self, master, imageFile):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.imageFile = imageFile
		self.createWidgets()
		self.pauseEvent = threading.Event()
		self.stopEvent = threading.Event()
		self.stopEvent.set()
		self.quitEvent = threading.Event()
		self.quitEvent.clear()
    
	def createWidgets(self):
		"""Build GUI."""
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.showMovie
		self.start.grid(row=1, column=0, padx=2, pady=2)

		# Create Puase button
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=1, padx=2, pady=2)

		# Create Resume button
		self.resume = Button(self.master, width=20, padx=3, pady=3)
		self.resume["text"] = "Resume"
		self.resume["command"] = self.resumeMovie
		self.resume.grid(row=1, column=2, padx=2, pady=2)
        
		# Create Stop Button
		self.stop = Button(self.master, width=20, padx=3, pady=3)
		self.stop["text"] = "Stop"
		self.stop["command"] = self.stopMovie
		self.stop.grid(row=1, column=3, padx=2, pady=2)
		
		# Create Exit button
		self.terminate = Button(self.master, width=20, padx=3, pady=3)
		self.terminate["text"] = "Exit"
		self.terminate["command"] =  self.exitClient
		self.terminate.grid(row=1, column=4, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=5, sticky=W+E+N+S, padx=5, pady=5) 
	
	def pauseMovie(self):
		"""Pause button handler."""
		if self.stopEvent.isSet():
			tkMessageBox.showerror("Pause", "Playback is currently stopped.")
		else:
			if self.pauseEvent.isSet() == False:
				self.pauseEvent.set()
				tkMessageBox.showinfo("Pause", "Video playback has been paused.")

	def resumeMovie(self):
		"""Resume button handler."""
		if self.stopEvent.isSet():
			tkMessageBox.showerror("Resume", "Playback is currently stopped.")
		elif self.pauseEvent.isSet():
			if tkMessageBox.askyesno("Resume", "Are you sure you want to resume playback?"):
				self.pauseEvent.clear() # Allows playback to resume

	def stopMovie(self):
		"""Stop button handler."""
		if self.stopEvent.isSet() == False:
			self.stopEvent.set()
			tkMessageBox.showinfo("Stop", "Playback has been stopped.")

	def exitClient(self):
		"""Exit button handler."""
		flag = 0
		if self.pauseEvent.isSet():
			flag = 1
		else:
			self.pauseEvent.set() # Ensure video is not playing before the question is displayed
		if tkMessageBox.askokcancel("Exit", "Are you sure you want to quit?"):
			if self.stopEvent.isSet() == False:
				self.quitEvent.set() # The other thread will clear this event variable just before it terminates
				self.stopEvent.set() # Video playback needs to be stopped first
				self.quitEvent.wait() # Ensure that the thread responsible for reading the video file terminates first
			self.master.destroy() # Close the GUI window
		elif flag == 0:
			self.pauseEvent.clear() # Allow playback to resume if video was playing beforehand
	
	def showMovie(self):
		"""Play button handler."""
		if self.stopEvent.isSet() == True:
			if tkMessageBox.askokcancel("Play", "Click OK to continue."):
				threading.Thread(target=self.updateScreen).start()

	def updateScreen(self):
		"""This function is run in a separate thread. It is responsible for managing playback. Event variables are used to tell it when to pause/resume/stop playback"""
		try:
			file1 = open(self.imageFile, "rb")
		except:
			tkMessageBox.showerror('Play', '"' + self.imageFile + '" could not be played.')
			exit()

		# Reset event variables for tracking playing/paused/stopped states
		self.pauseEvent.clear()
		self.stopEvent.clear()

		counter = 0
		while 1:
			val = file1.read(5) # Read the next 5 byte header
			if val == '': # End of video file has been reached
				self.stopEvent.set() # Playback has finished
				tkMessageBox.showinfo("Play", "Playback has finished.")
				file1.close()
				exit()
			data = file1.read(int(val)) # Read the current JPEG image
			counter += 1
			temp_file_name = str(counter) + ".jpeg"
			file2 = open(temp_file_name, "wb")
			file2.write(data)
			file2.close()
			time.sleep(0.035)
			photo = ImageTk.PhotoImage(Image.open(temp_file_name))
			self.label.configure(image = photo, height=288)
			self.label.image = photo
			os.remove(temp_file_name) # Comment out this line if you want the extracted JPEG images to remain on disk after playback finishes.
			while self.pauseEvent.isSet(): # Pause playback until an Exit, Resume or Stop command is issued
				
				# Case where an Exit or Stop command is issued whilst playback has been paused
				if self.stopEvent.isSet():
					file1.close()
					self.quitEvent.clear() # Inform the main thread that it may proceed to close the Pirate GUI window.
					exit() # Kill the playback thread only
				
				pass # Keep looping
			
			# Case where an Stop command is issued during playback
			if self.stopEvent.isSet():
				file1.close()
				self.quitEvent.clear() # Inform the main thread that it may proceed to close the Pirate GUI window.
				exit() # Kill the playback thread only

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.exitClient()
