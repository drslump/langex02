#!/usr/bin/python
# Manages snippet posting
#
#   - Requires an user name (via Http server)
#   - Input (POST)
#     - code:string    -> The code of the snippet
#     - language:string   -> If set this must be the language of the snippet
#        
#   Create a file at $data/:user/snippet

import json
import datetime
import cgitb
import cgi
import os
import sys
import uuid


cgitb.enable()

# Read the configuration file
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

configFile= open( '../conf/config.json', 'rb')
configuration= json.load( configFile)
#print configuration
dataPath= configuration[ "paths"]["data"]
#print configuration[ "paths"]["data"]

env = os.environ
#print "ENV=",env
#"<br/>".join( [ "%s=%s" % k,v for (k,v) in os.environ] )
if "REMOTE_USER" not in env:
    print "<H1>Error</H1>"
    print "Missing REMOTE_USER"
    sys.exit()

user= env["REMOTE_USER"]

# Make sure the directory is available

dataPath= os.path.join( dataPath, os.path.join( user, "snippet"))
if not os.path.isdir( dataPath):
    # create the directory
    os.makedirs( dataPath)

#if not env[ "REQUEST_METHOD" ] == "POST":
#    print "<H1>Error</H1>"
#    print "only POST method allowed."
#    sys.exit()
dt= datetime.datetime.utcnow().strftime( "%Y%m%d%H%M-")

form = cgi.FieldStorage()

if "code" not in form or "language" not in form:
    print "<H1>Error</H1>"
    print "Please fill in the code and language fields."
    sys.exit()

snippet={ }
#snippet={ "language": "", "code": ""}
snippet[ "language"]= form["language"].value
snippet[ "code"]= form["code"].value
#print "<p>language:", snippet[ "language"]
#print "<p>code:", snippet[ "code"]

#print "<br/>json dump", json.dumps( snippet)
snippetUUID= str(uuid.uuid1())
filename= os.path.join( dataPath, "".join( (dt, snippetUUID, ".json")))
#print "filename=", filename

output= open( filename, "wb")
output.write( json.dumps( snippet))
output.close()
