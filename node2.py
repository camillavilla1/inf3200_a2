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
		self.ip = 		ip
		self.port = 		port
		self.address = 		str(self.ip) + ":" + str(self.port)
		self.successor =	""
		self.predecessor = 	""

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

	def print_neighbours(self):
		print "successor: %s, predecessor: %s" % (self.successor, self.predecessor)
			

	def add(self, ip, port):
		if self.ip == 'localhost':
			commandline = "./node2.py --port=%d --creator=%s" % (port, self.address)

		process = subprocess.Popen(commandline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		newnode_address = "localhost"+":"+str(port)
		#Set successor to new node
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


		pass

	def do_PUT(self):
		pass
	
	def do_POST(self):
		key = self.extract_key_from_path(self.path)
		
		self.send_response(200)
		self.end_headers()
		

		if (key == "firstNode"):
			ip, port = find_free_ip(first_node=True)
			global node
			node = Node(ip, port)
			node.set_successor(node.address)
			node.set_predecessor(node.address)
			self.wfile.write("Initiated node on %s:%s \n " % (str(ip), str(port)))

		if (key == "addNode"):
			ip, port = find_free_ip()
			node.add(ip, port)
			self.wfile.write("Initiated node on %s:%s \n " % (str(ip), str(port)))
	
		
		#pass


def find_free_ip(first_node=False, n_port=8080):
	if (first_node == True):
		ip = "localhost"
		n_port = 8080
		return ip, n_port
	else:
		ip = "localhost"
		n_port = n_port + 1
		return ip, n_port


def parse_args():
	PORT_DEFAULT = 8080
	parser = argparse.ArgumentParser(prog="node", description="Node in a cluster")
	
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
		ip, port = find_free_ip(port=args.port)
		node = Node(ip, port)

		new_succ = node.get_creator_successor(args.creator)
		node.set_successor(new_succ)
		node.set_predecessor(args.creator)

		print "Node created on %s:%s \n" % (str(ip), str(port))
	

	try:
		server = ThreadedHTTPServer(('', args.port), Handler)
	except socket.error, exc:
		print ("Caught exception socket.eroor: %s" % exc)
		#args.port += 1

	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()

	def run_server():
		print 'Starting server, use <Ctrl-C> to stop'
		server.serve_forever()
		print "Server has shut down"

	def shutdown_server_on_signal(signum, fram):
		print "We get signal (%s). Asking server to shut down" % signum
		server.shutdown()
	
	thread = threading.Thread(target=server)
	thread.daemon = True
	thread.start()



	signal.signal(signal.SIGTERM, shutdown_server_on_signal)
	signal.signal(signal.SIGINT, shutdown_server_on_signal)




