#!/usr/bin/env python3
import atexit
import http.server
import inspect
import json
import os
import socketserver
import traceback
from importlib import reload
import wrapper
import lab

################################################################################
################################################################################
# RPCServerHandler

previous_json_string = None

class RPCServerHandler(http.server.SimpleHTTPRequestHandler):
    functions = {}
    redirects = {}
    modules = []
    path = ""

    def do_GET(self):
        path = self.path.lstrip('/').split('?')[0]
        print("GET: ", path)

        # Check if the file is in the redirects table.
        if path in self.redirects:
            path_to = self.redirects[path]
            print("REDIRECT TO ", path_to)
            self.send_response(301)
            self.send_header('location', path_to)
            self.end_headers()
            return True
        else:
            # serve the file!
            self.path = path
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        global previous_json_string
        path = self.path.lstrip('/').split('?')[0]
        if path in self.functions:
            try:
                content_type = self.headers.get('content-type')
                if 'application/json' not in content_type.lower():
                    raise ValueError("PUSH data doesn't look like json. Needs application/json content type.")
                content_len = int(self.headers.get('content-length', 0))
                json_string = self.rfile.read(content_len)
                json_data = json.loads(json_string.decode())

                try: # normal case
                    json_data = self.functions[path](json_data)
                    json_string = json.dumps(json_data)
                    previous_json_string = json_string

                except lab.NotEnoughMoneyError:
                    print ("Error: Not enough money to hire this zookeeper!")
                    json_string = previous_json_string
                    pass # just move on with the game

                finally:
                    self.send_response(200, 'OK')
                    self.send_header('Content-Type', 'application/json; charset=UTF-8')
                    self.end_headers()
                    self.wfile.write(bytes(json_string, 'utf-8'))

            except:
                # Throw a 500, print out error.
                traceback.print_exc()
                print("SOMETHING CRASHED! See above:")
                self.send_response(500, 'Internal error')

        else:
            self.send_error(404, 'function not found: ' + path +
                            " , while registered functions are: " + str(self.functions))

    @classmethod
    def register_function(cls, function, name):
        cls.functions[name] = function

    @classmethod
    def register_redirect(cls, path_from, path_to):
        cls.redirects[path_from] = path_to

    @classmethod
    def register_module(cls, module_name):
        cls.modules.append(module_name)

    @classmethod
    def reload_modules(cls):
        for module_name in cls.modules:
            print("in module %s ..." % module_name)
            module = __import__(module_name)
            reload(module)
            for f_name in dir(module):
                f = getattr(module, f_name)
                # names beginning with _ are hidden
                if f_name.startswith('_'):
                    continue
                # non-functions are ignored
                if not inspect.isfunction(f):
                    continue
                print("registering function %s" % f_name)
                cls.register_function(f, f_name)

################################################################################
################################################################################

# Initialize all the things!
PORT = 8000
handler = RPCServerHandler
httpd = socketserver.ThreadingTCPServer(("localhost", PORT), handler, False)
httpd.allow_reuse_address = True
httpd.server_bind()
httpd.server_activate()


# Code to list and serve files.
def ls_path(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def cat_file(path):
    with open(path, "r") as f:
        file = f.read()
    return file

def load_json_file(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

def cleanup():
    # Free the socket.
    print("CLEANING UP!")
    httpd.shutdown()
    print("CLEANED UP")

# ----------------------------------
# STATIC FILES: GET any path relative to PWD
# ----------------------------------
# redirect "/" to "static/index.html"
RPCServerHandler.register_redirect("", "/ui/index.html")

# ----------------------------------
# RPC API (POST)
# ----------------------------------
# restart: reload student code
# returns None
RPCServerHandler.register_function(lambda d: RPCServerHandler.reload_modules(), 'restart')

# ls: list directory contents
# returns a dictionary { directories: ["abc",...], files: ["abc",..] }
RPCServerHandler.register_function(lambda d: ls_path(d['path']), 'ls')

# cat: read contents of a file
# returns string contents of file
RPCServerHandler.register_function(lambda d: cat_file(d['path']), 'cat')

# load_json: read json object from a file
# returns json object encoded by a file
RPCServerHandler.register_function(lambda d: load_json_file(d['path']), 'load_json')

# call: call student code
# returns return value
RPCServerHandler.register_module("wrapper")
# ----------------------------------

atexit.register(cleanup)

# Start the server.
print("serving files and RPCs at port", PORT)
httpd.serve_forever()
