#!/usr/bin/python
# Updates the public profile of a user
#
#   - Input (POST)
#     - filename:string -> Path to the file with the task details
#        
#   Create a file at public/:user/profile.json

import hashlib
import json
import datetime
import os
import sys
import uuid

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

# Make sure the file is available
if not os.access( taskFilename, os.R_OK):
    print "Unable to access file", taskFilename
    sys.exit( 2)

# Load the task
task= json.load( open( taskFilename, "rb"))

# Load the private profile
profileFilename= os.path.join( dataPath, task["user"], "profile.json")
profile= json.load( open( profileFilename, "rb"))

# Build the public profile from the private profile
publicProfile= { "user": task[ "user"] }
if "avatar" in profile:
    publicProfile[ "avatar"]= profile[ "avatar"]
if "email" in profile:
    publicProfile[ "gravatar"]= hashlib.md5( profile[ "email"]).hexdigest()
if "site" in profile:
    publicProfile[ "site"]= profile[ "site"]

# Dump JSON
file= open( os.path.join( publicPath, "users", task[ "user"], "profile.json"), "wb")
file.write( json.dumps( publicProfile))
file.close()

