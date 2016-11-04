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

global node

class Node():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = str(self.ip) + ":" + str(self.port)
        self.successor = ""
        self.predecessor = ""
        self.neighbours = [self.successor, self.predecessor]

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

    def update_connections(self, new_successor):

        pass



    def print_neighbours(self):
        print "successor: %s, predecessor: %s" % (self.successor, self.predecessor)


    def add(self, ip, port):
        if self.ip == 'localhost':
            commandline = "./node2.py --port=%d --creator=%s" % (port, self.address)
        else:
            print "choosing second version of commandline!!!"
            commandline = "./node2.py --ip=%s --port=%d --creator=%s" % (ip, port, self.address)

        process = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        self.end_headers()
        if (key == 'get_creator_successor'):
            self.wfile.write(node.successor)	

        if (key == 'get_creator_predecessor'):
            self.wfile.write(node.predecessor)

        if (key == 'neighbours'):
            neighbours = "%s\n%s" % (node.predecessor, node.successor)
            print ("[GET] node ip: %s, node port: %s, [address: %s]" % (node.ip, node.port, node.address))
            print "Neighbours: [", neighbours,"]"
            #self.send_response(200)
            #self.end_headers()
            #neighbours =  threading.currentThread().getName()
            self.wfile.write(neighbours)


    def do_PUT(self):
        pass

    def do_POST(self):
        key = self.extract_key_from_path(self.path)

        self.send_response(200)
        self.end_headers()


        if (key == "firstNode"):
            ip, port = find_free_ip(first_node=True)
            print "port: %d" % port
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
            global node
            node.add(ip, port)

            self.wfile.write("Initiated node on %s:%s \n " % (str(ip), str(port)))
            node.update_connections(address)

        if (key == "update_predecessor"):
            print "inside update_predecessor"
            address = self.rfile.read()
            node.set_predecessor(address)
            self.wfile.write("Updated predecessor\n")




def find_free_ip(first_node=False):
    
    commandline = "sh find_node.sh 1"
    process = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()

    ip = output[0]
    ip = ip.strip(' \n')
    port = 8088

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

    if args.creator:
        ip, port = find_free_ip()
        node = Node(ip, port)

        new_succ = node.get_creator_successor(args.creator)
        node.set_successor(new_succ)
        node.set_predecessor(args.creator)
        # Updated the successor of this node, by setting the
        # predecessor value of the successor to the current node!
        node.update_successor(new_succ)

        print "Node created on %s:%s \n" % (str(ip), str(port))
    else:
        node = Node(args.ip, args.port)
        node.set_successor(node.address)
        node.set_predecessor(node.address)
        print node.address

    try:
        print "node IP : %s" % node.ip
        print "node HOST: %s" % node.port
        server = ThreadedHTTPServer((node.ip, node.port), Handler)
        print "Server started!!"
    except socket.error, exc:
        print ("Caught exception socket.error: %s" % exc)
        #args.port += 1

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

    thread.join(20*60)
    if thread.isAlive():
        print "Reached %.3f second timeout. Asking server to shut down" % 20*60
        server.shutdown()

    print "Exited cleanly"


