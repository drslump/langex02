#!/usr/bin/python
# Updates the tags related to a snippet
#
#   - Input (POST)
#     - filename:string -> Path to the file with the task details
#        
#   Create a file at $data/:user/snippet

# Get the list of all the file tags to update

# for each tag

# read the file

# add the entry to the top

# limit the file to TAG_MAX_ENTRIES


import hashlib
import json
import os
import sys
import smtplib


def addSnippet( filename, snippet, profile):
    "add a snippet to a file, including info from the author's profile"
    if not os.access( filename, os.F_OK) or not os.access( filename, os.W_OK):
        print "file does not exists:", filename
        file= open( filename, "wb") 
        entries=[]
    else:
        print "reading file", filename
        file= open( filename, "r+b")
        entries= json.load( file)
        file.seek( 0)
        print ",".join( ("tagFilename:", filename, "entries:", str(entries)))
    snippet[ "user"]= task[ "user"]
    if "site" in profile :
        snippet[ "site"]= profile[ "site"]
    if "avatar" in profile :
        snippet[ "avatar"]= profile[ "avatar"]
    if "email" in profile:
        snippet[ "gravatar"]= hashlib.md5( profile[ "email"]).hexdigest()
    entries.insert( 0, snippet)
    # TODO: limit the size of the feeds
    print "updated entries:" , entries
    file.write( json.dumps( entries))
    file.close()



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

# Load the snippet
snippetFilename= os.path.join( dataPath, task["user"], "snippet", task[ "id"])
if not os.path.exists( snippetFilename) or not os.access( snippetFilename, os.R_OK):
    print "Unable to access snippet file", snippetFilename
    sys.exit( 3)
file= open( snippetFilename, "rb")
snippet= json.load( file)
file.close()
if not "tags" in snippet:
    sys.exit( 0)

profileFilename= os.path.join( dataPath, task["user"], "profile.json")
profile= json.load( open( profileFilename, "rb"))
tags= snippet[ "tags"]

# Update every tag feed
for t in tags:
    tagDir= os.path.join( publicPath, "tags")
    # Build directory if it is missing
    if not os.path.exists( tagDir) or not os.path.isdir( tagDir):
        os.makedirs( tagDir)
    tagFilename= os.path.join( tagDir, ".".join( (t, "json")))
    print "Updating feed for tag", t

    addSnippet( tagFilename, snippet, profile)

# Update global snippets file
print "Updating global feed of snippets"
globalSnippetFilename= os.path.join( publicPath, "snippets.json")
addSnippet( globalSnippetFilename, snippet, profile)

# Update user snippets file
print "Updating feed of user snippets"
userSnippetFilename= os.path.join( publicPath, "users", task["user"], "snippets.json")
addSnippet( userSnippetFilename, snippet, profile)

# Update tags
print "Updating list of all tags"
tagsFilename= os.path.join( publicPath, "tags.json")
if not os.path.exists( tagsFilename):
    tagList=[]
else:
    tagsFile= open( tagsFilename, "rb")
    tagList= json.load( tagsFile)
    tagsFile.close()

# insert new tags
tagList.extend( snippet[ "tags"])

# Eliminate duplicates
uniqTagList= list( set( tagList) )

# Write the file
tagsFile= open( tagsFilename, "wb")
tagsFile.write( json.dumps( uniqTagList))
tagsFile.close()

# Send an email to all the friends of an author
for friend in profile[ "friends"]:
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
        msg['Subject'] = '%s has uploaded a new snippet' % task[ "user"]
        msg['From'] = me
        msg['To'] = you

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nThis is the snippet %s has uploaded\n\n%s" \
                % ( task["user"], snippet[ "code"] )
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               This is the snippet %s has uploaded<br>
            </p>
            <pre>%s</pre>
          </body>
        </html>
        """ % ( task["user"], snippet[ "code"] )

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

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

