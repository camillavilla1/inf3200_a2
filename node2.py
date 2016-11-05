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
        #conn.request('POST', '/update_predecessor', node.address)
        conn.request('PUT', '/update_predecessor', node.address)
        conn.getresponse()
        conn.close()

    def update_predecessor(self, c_address):
        conn = httplib.HTTPConnection(c_address)
        #conn.request('POST', '/update_successor', node.address)
        conn.request('PUT', '/update_successor', node.address)
        conn.getresponse()
        conn.close()

    def update_connections(self, new_successor, new_predecessor):
        self.successor = new_successor
        #self.set_successor(new_successor)
        self.predecessor = new_predecessor
        #self.set_predecessor(new_predecessor)

        #update conn to the new node, set succ and prede
        #node.successor = new_successor
        print "Current node adr: %s and [succ = %s] [pred = %s]" % (self.address, self.successor, self.predecessor)


    def print_neighbours(self):
        print "successor: %s, predecessor: %s" % (self.successor, self.predecessor)


    def add(self, ip, port, wait=False):
        if self.ip == 'localhost':
            commandline = "./node2.py --port=%d --creator=%s" % (port, self.address)
        else:
            cwd = os.getcwd()
            #print cwd
            #print "choosing second version of commandline!!!"
            commandline = "./node2.py --ip=%s --port=%d --creator=%s" % (ip, port, self.address)
            commandline = "ssh -f %s 'cd %s; %s'" % (ip, cwd, commandline)
            #print commandline

        #process = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = subprocess.Popen(commandline, shell=True, stdout=None, stderr=None)

        if wait:
            process.wait()

        # while(node.response==0):
            # pass
        # self.response = 0

        newnode_address = ip+":"+str(port)
        self.successor = newnode_address

        if self.predecessor == self.address:
            self.predecessor = newnode_address
        self.print_neighbours()



class Handler(BaseHTTPRequestHandler):
    def extract_key_from_path(self, path):
        return re.sub(r'/?(\w+)', r'\1', path)

    def do_GET(self):
        key = self.extract_key_from_path(self.path)

        self.send_response(200)
        self.send_header('Content-type', 'text\plain')
        self.end_headers()
        if (key == 'get_creator_successor'):
            print "Inside get_creator_successor"
            self.wfile.write(node.successor)	

        if (key == 'get_creator_predecessor'):
            print "Insidet get_creator_predecessor"
            self.wfile.write(node.predecessor)

        if (key == 'neighbours'):
            #neighbours = "%s\n%s" % (node.predecessor, node.successor)
            neighbours_list = []
            neighbours_list.append(node.predecessor)
            neighbours_list.append(node.successor)
            print "neighbour list: %s" % neighbours_list
            print ("[GET] [address: %s]" % node.address)

            #neighbours =  threading.currentThread().getName()
            #self.wfile.write(neighbours)
            self.wfile.write("\n".join(sorted(set(neighbours_list))))


    def do_PUT(self):
        key = self.extract_key_from_path(self.path)
        value = self.rfile.read()

        self.send_response(200)
        self.end_headers()

        if key == "update_port":
            value = value.split(":")
            port = value[1]
            print port

            #node.port = port

        # if (key == "update_predecessor"):
            # print "inside update_predecessor"
            # #print "address: %s" % address
            # address = self.rfile.read()
            # print "Address:"
            # print address
            # node.set_predecessor(address)
            # node.response = 1
            # self.wfile.write("Updated predecessor\n")

        # if (key == "update_successor"):
            # print "inside update_successor"

            # address = self.rfile.read()
            # print "Address:"
            # print address
            # node.set_successor(address)
            # node.response = 1
            # self.wfile.write("Updated successor\n")
            



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
            self.wfile.write("Initiated node on %s\n " % node.address)

        if (key == "addNode"):
            print "inside addNode"
            ip, port = find_free_ip()
            address = ip + ":" + str(port)
            print address
            #global node
            node.add(ip, port)
            #time.sleep(2000)
            tmp = ip + ":"+ str(port)
            #tmp = node.successor
            self.wfile.write(tmp)
            #self.wfile.write("Initiated node on %s:%s \n " % (str(ip), str(port)))
            print "Added node, should update connections"
            #node.update_connections(address, node.predecessor)

        if (key == "update_predecessor"):
            print "inside update_predecessor"
            #print "address: %s" % address
            address = self.rfile.read()
            print "Address:"
            print address
            node.set_predecessor(address)
            self.wfile.write("Updated predecessor\n")

        if (key == "update_successor"):
            print "inside update_successor"

            address = self.rfile.read()
            print "Address:"
            print address
            node.set_successor(address)
            self.wfile.write("Updated successor\n")
            




def find_free_ip(first_node=False):
    
    commandline = "sh find_node.sh 1"
    process = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()

    ip = output[0]
    ip = ip.strip(' \n')
    port = 8088
    #port = 45763

    return ip, port

    # if (first_node == True):
        # ip = "localhost"
        # n_port = 8080
        # return ip, n_port
    # else:
        # ip = "localhost"
        # global port
        # port = port + 1
        # return ip, port


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
        #ip, port = find_free_ip()
        #node = Node(ip, port)
        newip= args.ip
        newport = args.port

        #node.set_successor(new_succ)
        #node.set_predecessor(args.creator)
        # Updated the successor of this node, by setting the
        # predecessor value of the successor to the current node!

    else:
        #node = Node(args.ip, args.port)
        newip = args.ip
        newport = args.port

    server = None

    while server is None:
        try:
            #print "node IP : %s" % node.ip
            #print "node HOST: %s" % node.port
            server = ThreadedHTTPServer((newip, newport), Handler)
            print "Server started!!"
        except socket.error, exc:
            print ("Caught exception socket.error: %s" % exc)
            newport += 1
            #args.port += 1

    if args.creator:
        node = Node(newip, newport)
        new_succ = node.get_creators_successor(args.creator)
        node.update_connections(new_succ, args.creator)
        node.update_successor(new_succ)
        node.update_predecessor(args.creator)
        #node.print_neighbours()
        print "Node created on %s:%s \n" % (str(ip), str(port))

        conn = httplib.HTTPConnection(args.creator)
        conn.request('PUT', '/update_port', node.address)
        conn.getresponse()
        conn.close()


    else:
        node = Node(newip, newport)
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

    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()




    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)

    thread.join(60)
    if thread.isAlive():
        print "Reached %.3f second timeout. Asking server to shut down" % 60
        server.shutdown()

    print "Exited cleanly"


