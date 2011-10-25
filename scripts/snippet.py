#!/usr/bin/python
# Manages snippet posting
#
#   - Requires an user name (via Http server)
#   - Input (POST)
#     - code:string    -> The code of the snippet
#     - title:string   -> Title of the snippet
#     - language:string   -> If set this must be the language of the snippet
#     - tags:string   -> If set this must be a comma-separated list of tags
#        
#   Create a file at $data/:user/snippet

import json
import datetime
import time
import cgitb
import cgi
import os
import sys
import uuid

headers=[]

def print_headers():
    print "\n".join( [ h for h in headers ] )
    print

cgitb.enable()

headers.append( "Content-Type: text/html")
# Read the configuration file

configFile= open( '../conf/config.json', 'rb')
configuration= json.load( configFile)
#print configuration
dataPath= configuration[ "paths"]["data"]
tasksPath= configuration[ "paths"]["tasks"]
#print configuration[ "paths"]["data"]

env = os.environ
#print "ENV=",env
#"<br/>".join( [ "%s=%s" % k,v for (k,v) in os.environ] )
if "REMOTE_USER" not in env:
    headers.append('WWW-Authenticate: Basic realm="Langex"');
    headers.append('Status: 401 Unauthorized');
    headers.append('HTTP/1.0 401 Unauthorized');

    print_headers( )
    print "<H1>Error</H1>"
    print "Missing REMOTE_USER"
    sys.exit()

user= env["REMOTE_USER"]

# Make sure the directory is available

snippetPath= os.path.join( dataPath, user, "snippet")
if not os.path.isdir( snippetPath):
    # create the directory
    os.makedirs( snippetPath)

#if not env[ "REQUEST_METHOD" ] == "POST":
#    print "<H1>Error</H1>"
#    print "only POST method allowed."
#    sys.exit()
dt= datetime.datetime.utcnow().strftime( "%Y%m%d%H%M-")

form = cgi.FieldStorage()

if "code" not in form or "title" not in form:
#if "code" not in form or "language" not in form:
    headers.append('Status: 400');
    print_headers()
    print "<H1>Error</H1>"
    print "Please fill in the code and the title fields."
    sys.exit()

snippet={ "language": "", "author": "", "code": "", "title": "", "timestamp": "", "tags": []}
snippet[ "author"]= user
snippet[ "title"]= form["title"].value
snippet[ "code"]= form["code"].value
snippet[ "timestamp"]= int( time.mktime( datetime.datetime.utcnow().timetuple()))

if "tags" in form:
    snippet[ "tags"]= form["tags"].value.split( ",")
if "language" in form:
    snippet[ "language"]= form["language"].value

#print "<p>language:", snippet[ "language"]
#print "<p>code:", snippet[ "code"]

#print "<br/>json dump", json.dumps( snippet)
snippetUUID= "".join( (dt, str( uuid.uuid1()), ".json"))
filename= os.path.join( snippetPath, snippetUUID)
#print "filename=", filename

output= open( filename, "wb")
output.write( json.dumps( snippet))
output.close()

# Create a task for the snippet
filename= os.path.join( tasksPath, snippetUUID)
output= open( filename, "wb")
task= { "action": "snippet", "user": user, "id": snippetUUID }
output.write( json.dumps( task))
output.close()

# Create a task to notify friends
profileFilename= os.path.join( dataPath, user, "profile.json")
profile= json.load( open( profileFilename, "rb"))

filename= os.path.join( tasksPath, "-".join( ('notify',snippetUUID)))
output= open( filename, "wb")
task= { "action": "notify", "user": user, "id": snippetUUID }

if "friends" in profile:
# in case the user has friends notify them
   task["friends"]= profile["friends"]
   task["message"]= { \
       'subject': '%s has uploaded a new snippet' % user, \
       'text':    "Hi!\nThis is the snippet %s has uploaded\n\n%s", \
       'html':    """\
            <html>
              <head></head>
              <body>
                <p>Hi!<br>
                   This is the snippet %s has uploaded<br>
                </p>
                <pre>%s</pre>                                     
              </body>                                             
            </html>                                               
            """ % ( user, snippet[ "code"] )\
        }

output.write( json.dumps( task))
output.close()

print_headers()
print "OK"
