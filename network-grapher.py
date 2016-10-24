#!/usr/bin/env python

import collections
import httplib
import unittest

def fetch_neighbors(hostport):
    conn = httplib.HTTPConnection(hostport)
    conn.request("GET", "/neighbours")
    r1 = conn.getresponse()
    data1 = r1.read()
    if r1.status != 200:
        raise RuntimeError("Error {0} {1} from {2}".format(r1.status, r1.reason, hostport))
    else:
        return parse_neighbors(data1)

def parse_neighbors(neighborstring):
    stripped = neighborstring.strip()
    if stripped == '':
        return []
    else:
        return stripped.split("\n")

class ParseTests(unittest.TestCase):
    def test_zero_neighbors(self):
        self.assertEqual(
                parse_neighbors(""),
                [])

    def test_one_neighbor(self):
        self.assertEqual(
                parse_neighbors("localhost:8000"),
                ["localhost:8000"])

    def test_two_neighbors(self):
        self.assertEqual(
                parse_neighbors("localhost:8000\nlocalhost:8001"),
                ["localhost:8000", "localhost:8001"])

    def test_three_neighbors(self):
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
            neighbors = fetch_neighbors(server)
            graph[server] = neighbors
            for n in neighbors:
                if n not in graph:
                    print "new node {0}".format(n)
                    to_check.append(n)
    return graph

def print_graph(graph):
    for server,neighbors in graph.iteritems():
        print "{0} -> {{ {1} }}".format(server, ",".join(neighbors))

if __name__ == "__main__":

    hostport = "localhost:8000"
    graph = probe_network([hostport])
    print_graph(graph)
