#COMP5416 Assignment1 - client.py
#Yahong Liu

from socket import *
from time import *
from datetime import *
from sys import *

serverAddress = argv[1]
portNumber = int(argv[2])
pingTimes = int(argv[3])

RTTarray = [] # Array list to record the round trip time

j = 0 # Count number when there is a response from the server

# Request loop
for i in range(pingTimes) :

	clientSocket = socket(AF_INET, SOCK_DGRAM)
	message = '%d ping request' % (i)
	
	# Send message to the server
	try:

		clientSocket.settimeout(1) # Set the timeout to 1 second
		clientSocket.sendto(message, (serverAddress, portNumber))
		sendTime = datetime.now() # Get current time
		modifiedMessage, recvServerAddress = clientSocket.recvfrom(2048)
		
	# When time run out
	except timeout as exception :

		print '%d Request timed out' % (i) 		
		clientSocket.close()

	# When the server response
	else:

		RTTmicro = (datetime.now() - sendTime).microseconds # Round trip time in microseconds
		RTTseconds = timedelta(microseconds = RTTmicro) # Roundtrip time in seconds
		RTTarray.append(RTTmicro) # Append the roundtrip time(microseconds) to the array
		j += 1 # Count number plus 1
		print 'From', recvServerAddress, ': message=\'%s\',' % modifiedMessage, 'RTT=%ss' % (RTTseconds)

RTTarray.sort() # Sort the array list in positive sequence

# Print  the statistics
print '\nThe minimum round trip time is: %ss' % timedelta( microseconds = RTTarray[0] )
print 'The maximum round trip time is: %ss' % timedelta( microseconds = RTTarray[j-1] )
print 'The average round trip time is: %ss' % timedelta( microseconds = ( sum(RTTarray) / (j-1) ) )
print 'The packet loss rate(in percentage) is: %d%%' % ( (pingTimes - j) * 100 / pingTimes )