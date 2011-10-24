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

# Read the configuration file

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

configFile= open( '../conf/config.json', 'rb')
configuration= json.load( configFile)
print configuration
print configuration[ "paths"]

env = os.environ
print "ENV=",env
#"<br/>".join( [ "%s=%s" % k,v for (k,v) in os.environ] )
if "REMOTE_USER" not in env or "REQUEST_METHOD" not in env:
    print "<H1>Error</H1>"
    print "Forbidden."
    sys.exit()

#if not env[ "REQUEST_METHOD" ] == "POST":
#    print "<H1>Error</H1>"
#    print "only POST method allowed."
#    sys.exit()
dt= datetime.datetime.utcnow().strftime( "%Y%m%d%H%M-")

cgitb.enable()

form = cgi.FieldStorage()

if "code" not in form or "language" not in form:
    print "<H1>Error</H1>"
    print "Please fill in the code and language fields."
    sys.exit()

snippet={ "language": "", "code": ""}
snippet[ "language"]= form["language"].value
snippet[ "code"]= form["code"].value
print "<p>language:", snippet[ "language"]
print "<p>code:", snippet[ "code"]


print "<br/>json dump", json.dumps( snippet)
snippetUUID= str(uuid.uuid1())
filename= "".join( (dt, snippetUUID, ".json"))
print "filename=", filename

output= open( filename, "wb")
output.write( json.dumps( snippet))
