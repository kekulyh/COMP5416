#COMP5416 ASSIGNMENT2
##Declaration:
#####Author: Yahong Liu 


This is assignment 2 of COMP5416. I finished all the tasks with the additional exercises.

##Folder explanation
###assignment2 - with task 4
This the complete code of all the tasks and the additional exercise.

###assignment2 - without task 4
This is the code of previous 3 tasks. Just in case of reviewing.

###mjpegmaker
This is the code for creating mjpeg file.


##Operating method:
###Server:
`./run_server.sh`

or

`python Server.py 3000 &`

###Client:
`./run_client.sh`

or

`python ClientLauncher.py 127.0.0.1 3000 12000 Sample.Mjpeg`

##Elaboration of Task4
###Question1:
RTP packet loss rate function is defined in ServerWorker.py. When the movie is finished, server side will print out the statistics.

```
# Task 4 question 1: RTP loss rate
rtpLossRate = self.rtpError*100/float(frameNbr)
print "RTP packet loss rate is: %.3f %%" %(rtpLossRate)
```

Video data rate function is defined in Client.py. Each frame of the movie will print out the data rate.

```
# Task 4 question 1: video data rate
dataRate = self.movieSize / self.timeConsume
print "Video Data Rate: %.3f byte/s" % dataRate
```

###Question2:
'Setup' and 'Play' function is combined together with PLAY button.

As for the TEARDOWN button, it depends on the user's custom. That's why this function is always an option in the preference settings. If user would like the STOP button to just stop playing but not quit the client, the only thing is to extract the quit function out of the button.



###Question3:
SETUP button is replaced with DESCRIBE button. The server sends back the description of the session.

