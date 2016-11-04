#!/usr/bin/env python

import argparse
import collections
import httplib
import socket
import unittest

def parse_args(args=None):
    parser = argparse.ArgumentParser(prog="network-grapher",
            description="Quick and dirty utility to find which nodes are connected to what other nodes")

    parser.add_argument("node",
            help="starter node to connect to first")

    return parser.parse_args()

def fetch_neighbors(hostport):
    conn = httplib.HTTPConnection(hostport)
    conn.request("GET", "/neighbours")
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()
    if r1.status != 200:
        print ("Status is not OK")
        raise RuntimeError("Error {0} {1} from {2}".format(r1.status, r1.reason, hostport))
    else:
        print "about to parse neighbours"
        return parse_neighbors(data1)

def parse_neighbors(neighborstring):
    stripped = neighborstring.strip()
    if stripped == '':
        return []
    else:
        return stripped.split("\n")

class ParseTests(unittest.TestCase):
    def test_zero_neighbors(self):
        print "zero neighbours"
        self.assertEqual(
                parse_neighbors(""),
                [])

    def test_one_neighbor(self):
        print "one neighbours"
        self.assertEqual(
                parse_neighbors("localhost:8000"),
                ["localhost:8000"])

    def test_two_neighbors(self):
        print "two neighbours"
        self.assertEqual(
                parse_neighbors("localhost:8000\nlocalhost:8001"),
                ["localhost:8000", "localhost:8001"])

    def test_three_neighbors(self):
        print "three neighbours"
        self.assertEqual(
                parse_neighbors("localhost:8000\nlocalhost:8001\nlocalhost:8002"),
                ["localhost:8000", "localhost:8001", "localhost:8002"])

def probe_network(known_servers):
    to_check = collections.deque(known_servers)
    checked = []
    graph = {}
    while len(to_check):
        server = to_check.popleft()
        if server not in graph:
            try:
                neighbors = fetch_neighbors(server)
                graph[server] = neighbors
                for n in neighbors:
                    if n not in graph:
                        to_check.append(n)
            except socket.error as e:
                graph[server] = e
    return graph

def print_graph(graph):
    for server,neighbors in graph.iteritems():
        if isinstance(neighbors, socket.error):
            print "{0} -> {1}".format(server, repr(neighbors))
        else:
            print "{0} -> {{ {1} }}".format(server, ",".join(neighbors))

if __name__ == "__main__":

    args = parse_args()
    graph = probe_network([args.node])
    print_graph(graph)
