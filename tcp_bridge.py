#!/usr/bin/env python

import gevent.monkey
from gevent.pool import Pool
gevent.monkey.patch_all()

import sys
import os
import socket


def usage():
    print "Usage: %s local_host:local_port remote_host:remote_port" % os.path.basename(__file__)

def get_addr(arg):
    return tuple(apply(*args) for args in zip((str, int), zip(arg.split(':'))))

def unidir(sin, sout):
    while True:
        buff = sin.recv(8192)
        if not buff:
            sout.close()
            sin.close()
            return
        sout.sendall(buff)

def bridge(sock, remote_addr):
    try:
        rsock = socket.create_connection(remote_addr)
        try:
            pool = Pool(2)
            pool.spawn(unidir, sock, rsock)
            pool.spawn(unidir, rsock, sock)
            pool.wait_available()
        finally:
            rsock.close()
    finally:
        sock.close()

if len(sys.argv) != 3:
    usage()
    sys.exit(2)

local_addr, remote_addr = map(get_addr, sys.argv[1:3])

server_sock = socket.socket()
server_sock.bind(local_addr)
server_sock.listen(1024)
while True:
    sock, addr = server_sock.accept()
    gevent.spawn(bridge, sock, remote_addr)
