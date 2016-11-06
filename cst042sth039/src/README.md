Test Utilities for INF-3200, Fall 2016, Assignment 2
=====================================================

This repository contains of two quick-and-dirty test clients for your project
networks.

- `test-client.py` -- Uses the network's API to connect to a single node and
  issue commands to fire up and shut down more nodes.
- `network-grapher.py` -- Uses the API to crawl the network and build a list of
  how the nodes are connected.

Each takes one argument, the node to connect to.

    ./test-client.py localhost:8000
    ./network-grapher.py localhost:8000

Like with the previous project, we will be using more thorough versions of these
utilities to test your network in action. We strongly suggest that you add your
own enhancements to these clients to perform more thorough tests. Think about
different scenarios and interesting corner cases:

- What happens as the network gets much larger?
- What happens as churn increases (faster joins and leaves)?
- What happens when multiple startup and shutdown requests are executed in
  parallel?

Hints
--------------------------------------------------

- Try running the `network-grapher` with the Unix `watch` command to re-run and
  print the output every few seconds.

        watch ./network-grapher.py localhost:8000

- With a little massaging, you might be able to get the `network-grapher` to
  print valid descriptions for [Graphviz]( http://www.graphviz.org/), or another
  visualization library, to get an actual graphical map of your network.



RUN THE PROGRAM

Open terminal and go to uvrocks
Locate directory and run
./node2.py --ip compute-X-X --port 8088

open another terminal and go to uvrocks
locate directory and run
./test-client.py compute-X-X:8088

./network-grapher.py compute-X-X:8088
