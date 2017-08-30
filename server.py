"""
Basic REST API
Supports:
adding new url to parse links
fetching list of parsed urls
fetching list of parsed links and count of their occurenses
"""

import SimpleHTTPServer
import SocketServer

PORT = 8000

class Handler()
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()