from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import re
import argparse
import httplib
import signal
import socket

nodeList = []
neighbors = []


class Node():
    pass


class Handler(BaseHTTPRequestHandler):
    def extract_key_from_path(self, path):
        return re.sub(r'/?(\w+)', r'\1', path)

    def do_GET(self):
        key = self.extract_key_from_path(self.path)
        
        if (key == "/neighbours"):
            #node.neighbours()
            #message = str(node.ip + node.port)
            pass



        self.send_response(200)
        self.end_headers()
        #message =  threading.currentThread().getName()
        message = "dildo"
        self.wfile.write(message)
        self.wfile.write('\n')
        return

    def do_POST(self):
        key = self.extract_key_from_path(self.path)
        self.send_response(200)
        self.end_headers()
        if (key == "/addNode"):
            #node.Add()
            pass
        if (key == "/shutdown"):
            #node.shutdown()
            pass
        

        message = ("/addNode\n")


        self.wfile.write(message)




class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('localhost', 8080), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()


    #before killing/shut down a node, we need to start a new thread?!
    #different threads must kill each other
