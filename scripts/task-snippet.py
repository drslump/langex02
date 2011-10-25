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
import datetime
import os
import sys
import uuid

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

