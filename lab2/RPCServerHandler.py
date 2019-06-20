import sys, json, traceback, inspect
import http.server
from types import ModuleType
from importlib import reload

class RPCServerHandler(http.server.SimpleHTTPRequestHandler):
  functions = {}
  redirects = {}
  modules = []

  def do_GET(self):
    path = self.path.lstrip('/').split('?')[0]
    print("GET: ", path)
    # is the file in the redirects table?
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
    path = self.path.lstrip('/').split('?')[0]
    if path in self.functions:
      try:
        content_type = self.headers.get('content-type')
        if not 'application/json' in content_type.lower():
          raise ValueError("PUSH data doesn't look like json. Needs application/json content type.")
        content_len = int(self.headers.get('content-length', 0))
        json_string = self.rfile.read(content_len)
        json_data = json.loads(json_string.decode())

        json_data = self.functions[path](json_data)
        json_string = json.dumps(json_data)

        self.send_response(200, 'OK')
        self.send_header('Content-Type', 'application/json; charset=UTF-8')
        self.end_headers()

        self.wfile.write(bytes(json_string,'utf-8'))
      except:
        # throw a 500, print out error
        traceback.print_exc();
        print("SOMETHING CRASHED! See above:")
        self.send_response(500, 'Internal error')
    else:
      self.send_error(404, 'function not found: ' + path + " , while registered functions are: " + str(self.functions))
    return

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

