"""
	File name: mjpegmaker.py
	Author: Yahong Liu
	Version: 2.0
	Date: 26/10/2015
	Description: COMP5416 Assignment2 mjpeg file maker
"""

#!/usr/bin/python
import os, sys, re, binascii

# Traversal through the files
def listFiles(dirPath):
	fileList=[]
	for root,dirs,files in os.walk(dirPath):
		for fileObj in files:
			fileList.append(os.path.join(root,fileObj))
	return fileList

def main():
	# picture folder
	fileDir = "pic/"
	# traversal the folder
	fileList = listFiles(fileDir)
	# loop: open the picture file
	for fileObj in fileList:
		
		f = open(fileObj,'rb')
		val = f.read()
		f.close()
		# open mjpeg file in append mode
		movie = open("movie.Mjpeg", "a")
		
		# size = str(sys.getsizeof(val)) # function sys.getsizeof is wrong
		size = str(len(val))
		# ensure the header size is 5 byte
		m = 5-len(size)
		if m>0:
			size = '0'*m +size

		# a = ''.join([str(ord(i)) for i in size])
		print "file: %s"%fileObj
		print "size decimal: " + size
		# print "ascii decimal: " + a
		# print "ascii hex: " + binascii.b2a_hex(size)

		# write the mjpeg file
		movie.write(size)
		movie.write(val)
		movie.close()

if __name__=='__main__':
	main()