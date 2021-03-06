# baed on http://stackoverflow.com/questions/14088294/multithreaded-web-server-in-python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import re
import argparse
import httplib
import signal
import socket
import os
import subprocess


nodeList = []
neighbours = []
cur_port = 8080


class Node():
    def __init__(self, ip, port):
        #pass
        #self.n_id = n_id
        self.created = 0
        self.creator = ""
        self.neighbours = []
        self.ip = ip
        self.port = port
        self.address = str(self.ip) + ":" + str(self.port)

    def add(self, stdout=subprocess.PIPE, stderr=subprocess.PIPE, wait=False):
        #like launch in launch.py in first assignment
        cwd = os.getcwd()
        if self.ip == 'localhost':
            commandline = "./node.py --port=%d --creator=%s" % (cur_port, self.address)
        else:
            commandline = "ssh -f %s 'cd %s; %s'" % (host, cwd, commandline)

        print(commandline)
        process = subprocess.Popen(commandline, shell=True, stdout=stdout, stderr=stderr)
        if wait:
            process.wait()

    def is_created(self, args):
        if (args.creator):
            self.created = 1
            self.creator = args.created
            self.neighbours.append(self.creator)
            
            # conn = httplib.HTTPConnection(self.creator)
            # conn.request('POST', '/update')
            # print "CREATOR U THERE MAYNE?"
            # # conn.request('PUT', '/info', (self.ip, self.port))
            # conn.getresponse()
            # conn.closer()


    def shutdown():
        shutdown_server_on_signal()
        #might notify neighbours

    def neighbours():
        pass

        #return list of ip:port pairs of all nodes 
        #that are connected to the recipent node   



class Handler(BaseHTTPRequestHandler):
    def extract_key_from_path(self, path):
        return re.sub(r'/?(\w+)', r'\1', path)

    def do_GET(self):
        key = self.extract_key_from_path(self.path)
        
        if (key == "/neighbours"):
            #node.neighbours()
            #message = str(node.ip + node.port)
            #responsebody "127.0.0.1:1234, 127.0.0.1:5678 ..."
            pass

        


        #self.send_response(200)
        #self.end_headers()
        #message =  threading.currentThread().getName()
        #message = "dildo"
        #self.wfile.write(message)
        #self.wfile.write('\n')
        #return


    def do_PUT(self):
        key = self.extract_key_from_path(self.path)
        #content_length = int(self.headers.getheader('content-length', 0))

        if (key == "info"):
            value = self.rfile.read()
            print value
            self.send_response(200)
            self.end_headers()

            node.neighbours.append(value)

            print node.neighbours
            


    def do_POST(self):
        key = self.extract_key_from_path(self.path)
        self.send_response(200)
        self.end_headers()
        if (key == "addNode"):
            #ode = Node("127.0.0.1", "8081")
            #n_ip, n_port = node.add()
            node.add()
            global cur_port
            
            #value = node.neighbours[-1]
            address = node.ip + ":" + str(cur_port)
            node.neighbours.append(address)

            self.wfile.write(address)
            cur_port += 1

        if (key == "update"):
            #print node.neighbours
            #self.wfile.write(node.neighbours)

            #node.add(node.host, "./node.py --port=%d --nameserver=%s" % (node.port, nameserver))
            #responsebody "127.0.0.1:1234"
        if (key == "shutdown"):
            node.shutdown()
        

        #message = (n_ip, n_port)


        #self.wfile.write(message)



def parse_args():
    #PORT_DEFAULT = 8080
    PORT_DEFAULT = cur_port
    DIE_AFTER_SECONDS_DEFAULT = 20 * 60
    parser = argparse.ArgumentParser(prog="node", description="DHT Node")

    parser.add_argument("-p", "--port", type=int, default=PORT_DEFAULT,
            help="port number to listen on, default %d" % PORT_DEFAULT)

    parser.add_argument("-c", "--creator", type=str)

    parser.add_argument("--die-after-seconds", type=float,
            default=DIE_AFTER_SECONDS_DEFAULT,
            help="kill server after so many seconds have elapsed, " +
                "in case we forget or fail to kill it, " +
                "default %d (%d minutes)" % (DIE_AFTER_SECONDS_DEFAULT, DIE_AFTER_SECONDS_DEFAULT/60))

    parser.add_argument("--nameserver", type=str, required=False,
            help="address (host:port) of nameserver to register with")

    return parser.parse_args()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""



if __name__ == '__main__':
    args = parse_args()
    address = "%s:%d" % (socket.gethostname(), args.port)

    node = Node("localhost", args.port)
    node.is_created(args)

    if (node.created == 0):
        cur_port += 1

    not_initiated = 1

    while (not_initiated):
        try:
            server = ThreadedHTTPServer(('', args.port), Handler)
            not_initiated = 0
        except socket.error, exc:
            print ("Caught exception socket.error : %s" % exc)
            args.port += 1



    #server = ThreadedHTTPServer(('localhost', 8080), Handler)
    def run_server():
        print 'Starting server, use <Ctrl-C> to stop'
        server.serve_forever()  
        print "Server has shut down"


    def shutdown_server_on_signal(signum, frame):
        print "We get signal (%s). Asking server to shut down" % signum
        server.shutdown()


    # Start server in a new thread, because server HTTPServer.serve_forever()
    # and HTTPServer.shutdown() must be called from separate threads
    #before killing/shut down a node, we need to start a new thread?!
    #different threads must kill each other
    thread = threading.Thread(target=server)
    #thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()

    # Shut down on kill (SIGTERM) and Ctrl-C (SIGINT)
    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)


    thread.join(args.die_after_seconds)
    if thread.isAlive():
        print "Reached %.3f second timeout. Asking server to shut down" % args.die_after_seconds
        server.shutdown()

    print "Exited cleanly"


    #nodes = Node()

    # Launch nodes
    #for node in nodes:
    #    launch(node.host, "./node.py --port=%d --nameserver=%s" % (node.port, nameserver))
          

