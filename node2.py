#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import time
import re
import argparse
import httplib
import signal
import socket
import os
import subprocess

global node

class Node():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = str(self.ip) + ":" + str(self.port)
        self.successor = ""
        self.predecessor = ""
        self.neighbours = [self.successor, self.predecessor]
        self.response = 0
        self.lastport = port
        self.server = None

    def set_successor(self, address):
        self.successor = address

    def set_predecessor(self, address):
        self.predecessor = address

    def get_creators_successor(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('GET', '/get_creator_successor')
        resp = conn.getresponse()
        conn.close()
        creator_successor = resp.read()
        return creator_successor

    def get_creators_predecessor(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('GET', '/get_creator_predecessor')
        resp = conn.getresponse()
        conn.close()
        creator_predecessor = resp.read()
        return creator_predecessor

    def update_successor(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('POST', '/update_predecessor', node.address)
        conn.getresponse()
        conn.close()

    def update_predecessor(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('POST', '/update_successor', node.address)
        conn.getresponse()
        conn.close()

    def update_predecessor_shutdown(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('POST', '/update_successor', node.successor)
        conn.getresponse()
        conn.close()

    def update_successor_shutdown(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('POST', '/update_predecessor', node.predecessor)
        conn.getresponse()
        conn.close()

    def update_neighbour(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        conn.request('POST', '/update_predecessor', c_address)
        conn.request('POST', '/update_successor', c_address)
        conn.getresponse()
        conn.close()


    def update_connections(self, new_successor, new_predecessor):
        self.successor = new_successor
        self.predecessor = new_predecessor
        print "Current node adr: %s and [succ = %s] [pred = %s]" % (self.address, self.successor, self.predecessor)

    def print_neighbours(self):
        print "successor: %s, predecessor: %s" % (self.successor, self.predecessor)

    def add(self, ip, port, wait=False):
        if self.ip == 'localhost':
            commandline = "./node2.py --port=%d --creator=%s" % (port, self.address)
        else:
            cwd = os.getcwd()
            commandline = "./node2.py --ip=%s --port=%d --creator=%s" % (ip, port, self.address)
            commandline = "ssh -f %s 'cd %s; %s'" % (ip, cwd, commandline)

        process = subprocess.Popen(commandline, shell=True, stdout=None, stderr=None)

        while(node.response == 0):
            pass
        self.response = 0

        newnode_address = ip+":"+str(self.lastport)
        self.successor = newnode_address

        if self.predecessor == self.address:
            self.predecessor = newnode_address
        self.print_neighbours()

        return self.successor

    def shutdown_server(self):
        if (self.successor != self.address):
            self.update_successor_shutdown(self.predecessor)
        if (self.predecessor != self.address):
            self.update_predecessor_shutdown(self.successor)

        #if (self.successor == self.predecessor and self.successor != self.address):
            #self.update_neighbour(self.successor)

        
            



class Handler(BaseHTTPRequestHandler):
    def extract_key_from_path(self, path):
        return re.sub(r'/?(\w+)', r'\1', path)

    def do_GET(self):
        key = self.extract_key_from_path(self.path)

        self.send_response(200)
        self.send_header('Content-type', 'text\plain')
        self.end_headers()
        if (key == 'get_creator_successor'):
            self.wfile.write(node.successor)	

        if (key == 'get_creator_predecessor'):
            self.wfile.write(node.predecessor)

        if (key == 'neighbours'):
            neighbours_list = []
            neighbours_list.append(node.predecessor)
            neighbours_list.append(node.successor)
            print "neighbour list: %s" % neighbours_list
            self.wfile.write("\n".join(sorted(set(neighbours_list))))


    def do_PUT(self):
        key = self.extract_key_from_path(self.path)

        node.response = 1
        node.lastport = int(key)

        self.send_response(200)
        self.end_headers()

        # if key == "update_port":
            # value = value.split(":")
            # port = value[1]
            # print port


    def do_POST(self):
        key = self.extract_key_from_path(self.path)

        self.send_response(200)
        self.end_headers()


        if (key == "firstNode"):
            ip, port = find_free_ip(first_node=True)
            #print "port: %d" % port
            global node
            node = Node(ip, port)
            node.set_successor(node.address)
            node.set_predecessor(node.address)
            print node.address

            # self.send_response(200)
            # self.end_headers()
            self.wfile.write("Initiated node on %s\n " % node.address)

        if (key == "addNode"):
            ip, port = find_free_ip()
            #address = ip + ":" + str(port)
            #global node
            address = node.add(ip, port)
            print address
            #time.sleep(2000)
            #tmp = node.successor

            # self.send_response(200)
            # self.end_headers()
            self.wfile.write(address)
            print "Added node, should update connections"
            #node.update_connections(address, node.predecessor)

        if (key == "update_predecessor"):
            address = self.rfile.read()
            print address
            node.set_predecessor(address)
            # self.send_response(200)
            # self.end_headers()
            self.wfile.write("Updated predecessor\n")
            print "Updated predeccessor for adr: %s" % address

        if (key == "update_successor"):
            address = self.rfile.read()
            node.set_successor(address)

            # self.send_response(200)
            # self.end_headers()
            self.wfile.write("Updated successor\n")
            print "Updated successor for adr: %s" % address

        if (key == "shutdown"):
            #address = self.rfile.read()
            #print "shutdown this nigga on adr %s" % address
            self.wfile.write("Server is shutting down")
            node.shutdown_server()
            #server.shutdown()
            #node.shutdown_server()
            #check neighbours before shutdown
            shutdown_specific_server(server)
            # self.send_response(200)
            # self.end_headers()




def find_free_ip(first_node=False):
    
    commandline = "sh find_node.sh 1"
    process = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()

    ip = output[0]
    ip = ip.strip(' \n')
    port = 8088

    return ip, port
    
def parse_args():
    PORT_DEFAULT = 8080
    parser = argparse.ArgumentParser(prog="node", description="Node in a cluster")

    parser.add_argument("-i", "--ip", type=str, default="localhost")

    parser.add_argument("-p", "--port", type=int, default=PORT_DEFAULT,
            help="port number to listen on, default %d" % PORT_DEFAULT)

    parser.add_argument("-c", "--creator", type=str,
            help="the creator of the node initiated") 

    return parser.parse_args()



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""




if __name__ == '__main__':
    args = parse_args()
    newip = ""
    newport = 0

    if args.creator:
        newip= args.ip
        newport = args.port
    else:
        newip = args.ip
        newport = args.port

    server = None

    while server is None:
        try:
            server = ThreadedHTTPServer((newip, newport), Handler)
            print "Server started!! on %s" % str(newip) + ":" + str(newport)
        except socket.error, exc:
            print ("Caught exception socket.error: %s" % exc)
            newport += 1
            #args.port += 1

    if args.creator:
        node = Node(newip, newport)
        node.server = server
        new_succ = node.get_creators_successor(args.creator)
        node.update_connections(new_succ, args.creator)
        node.update_successor(new_succ)
        
        conn = httplib.HTTPConnection(args.creator)
        conn.request("PUT", "/"+str(newport))
        conn.getresponse()
        conn.close()


        #node.update_predecessor(args.creator)
        #node.print_neighbours()
        print "Node created on %s:%s \n" % (str(newip), str(newport))
    else:
        node = Node(newip, newport)
        node.server = server
        node.set_successor(node.address)
        node.set_predecessor(node.address)
        print node.address

    def run_server():
        print 'Starting server, use <Ctrl-C> to stop'
        server.serve_forever()
        print "Server has shut down"

    def shutdown_server_on_signal(signum, fram):
        print "We get signal (%s). Asking server to shut down" % signum
        server.shutdown()

    def shutdown_specific_server(server):
        server.shutdown()    

    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()

    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)

    thread.join(10*60)
    if thread.isAlive():
        print "Reached %.3f second timeout. Asking server to shut down" % 60
        server.shutdown()

    print "Exited cleanly"


