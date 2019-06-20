#!/usr/bin/env python3
from RPCServerHandler import RPCServerHandler
import socketserver, os, atexit, json
import wrapper

# Initialize all the things
PORT = 8000
handler = RPCServerHandler
httpd = socketserver.ThreadingTCPServer(("localhost", PORT), handler, False)
httpd.allow_reuse_address = True
httpd.server_bind()
httpd.server_activate()

"""
# Register files in "resources" recursively
for root, dirnames, filenames in os.walk('resources'):
  for f in filenames:
    f = root + '/' + f
    print("ADDING : ", f, " : ", os.path.relpath(f, 'resources'))
    RPCServerHandler.register_file(f, os.path.relpath(f, 'resources'))
# Point '' to index.html
"""

# Code to list and serve files
def ls_path( path ):
  return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def cat_file( path ):
  file = ""
  with open(path, "r") as f:
    file = f.read()
  return file

def load_json_file( path ):
  data = None
  with open(path, "r") as f:
    data = json.load(f)
  return data

### ----------------------------------
### STATIC FILES: GET any path relative to PWD
### ----------------------------------
# redirrect "/" to "static/index.html"
RPCServerHandler.register_redirect("", "/ui/index.html")

### ----------------------------------
### RPC API (POST)
### ----------------------------------
# restart: reload student code
# returns None
RPCServerHandler.register_function(lambda d : RPCServerHandler.reload_modules(), 'restart')

# ls: list directory contents
# returns a dictionary { directories: ["abc",...], files: ["abc",..] }
RPCServerHandler.register_function(lambda d : ls_path( d['path']) , 'ls')

# cat: read contents of a file
# returns string contents of file
RPCServerHandler.register_function(lambda d : cat_file( d['path'] ), 'cat')

# load_json: read json object from a file
# returns json object encoded by a file
RPCServerHandler.register_function(lambda d : load_json_file( d['path'] ), 'load_json')

# call: call student code
# returns return value
RPCServerHandler.register_module("wrapper")
### ----------------------------------

def cleanup():
  # free the socket
  print("CLEANING UP!")
  httpd.shutdown()
  print("CLEANED UP")

atexit.register(cleanup)

# Start the server
print("serving files and RPCs at port", PORT)
httpd.serve_forever()
