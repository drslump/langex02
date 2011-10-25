#!/usr/bin/python
# Notify users by email
#
#   - Input (POST)
#     - filename:string -> Path to the file with the task details
#        
#   Send an email to each recipient

import hashlib
import json
import os
import sys
import smtplib

if len( sys.argv) < 2:
    print "usage: path_to_task_file"
    sys.exit( 1)

taskFilename= sys.argv[1]

configFile= open( '../conf/config.json', 'rb')
configuration= json.load( configFile)
configFile.close()

#print configuration
dataPath= configuration[ "paths"]["data"]
tasksPath= configuration[ "paths"]["tasks"]
publicPath= configuration[ "paths"]["public"]

# Make sure the directory is available
if not os.access( taskFilename, os.R_OK):
    print "Unable to access file", taskFilename
    sys.exit( 2)

# Load the task
task= json.load( open( taskFilename, "rb"))

# Send an email to all the friends of an author
for friend in task[ "friends"]:
    # Read friend profile
    friendProfileFilename= os.path.join( dataPath, friend, "profile.json")
    friendProfileFile= open( friendProfileFilename, "rb")
    friendProfile= json.load( friendProfileFile)
    # Check if the email is available
    if "email" in friendProfile:
        import smtplib

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # me == my email address
        # you == recipient's email address
        me = "socialcoding@tid.es"
        you = friendProfile[ "email"]

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = task['message']['subject']
        msg['From'] = me
        msg['To'] = you

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText( task['message']['text'], 'plain')
        part2 = MIMEText( task['message']['html'], 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP('mailhost.hi.inet')
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        result= s.sendmail(me, you, msg.as_string())
        print "Sending email to", you, "has this result:", result
        s.quit()

