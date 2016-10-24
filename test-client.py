#!/usr/bin/env python

import collections
import httplib
import sys
import time
import unittest


def start_new_node(via_node):
    sys.stdout.write("Asking {0} to start a new node... ".format(via_node))
    sys.stdout.flush()
    conn = httplib.HTTPConnection(via_node)
    conn.request("POST", "/addNode")
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()
    if r1.status != 200:
        print "Error {0} {1}".format(r1.status, r1.reason)
        raise RuntimeError("Startup: Error {0} {1} from {2}".format(
            r1.status, r1.reason, via_node))
    else:
        newnode = data1.strip()
        print "New node: {0}".format(newnode)
        return newnode.strip()

def shutdown_node(target_node):
    print "Asking {0} to shutdown...".format(target_node)
    conn = httplib.HTTPConnection(target_node)
    conn.request("POST", "/shutdown")
    r1 = conn.getresponse()
    data1 = r1.read()
    conn.close()
    if r1.status != 200:
        raise RuntimeError("Shutodwn: Error {0} {1} from {2}".format(
            r1.status, r1.reason, target_node))
    else:
        return data1.strip()

origin_node = None
spawned_nodes = set()

def start_many_via_origin(origin_node, count, wait=.2):
    print
    print "Starting up {0} nodes via {1}, with {2:.3f} second delay...".format(
            count, origin_node, wait)
    for i in range(0,count):
        newnode = start_new_node(via_node=origin_node)
        spawned_nodes.add(newnode)
        time.sleep(wait)

def shutdown_all(wait=.2):
    print
    print "Shutting down all nodes, with {0:.3f} second delay...".format(wait)
    while spawned_nodes:
        node = spawned_nodes.pop()
        shutdown_node(node)
        time.sleep(wait)

def print_status():
    if len(spawned_nodes) < 10:
        print "Origin: {0}, Spawned: [{1}]".format(
                origin_node, ",".join(spawned_nodes))
    else:
        print "Origin: {0}, Spawned: {1} nodes".format(
                origin_node, ",".join(spawned_nodes))

if __name__ == "__main__":

    origin_node = "localhost:8000"
    start_many_via_origin(origin_node, 5, wait=2)
    print_status()

    shutdown_all()
    print_status()
