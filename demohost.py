# Application ID: 65250674-7c32-4e98-a20d-86da2f73a22b

import http.server
import socketserver

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", 30662), Handler) as httpd:
    httpd.serve_forever()