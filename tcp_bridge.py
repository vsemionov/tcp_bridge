#!/usr/bin/env python

# Copyright (C) 2011 Victor Semionov
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the copyright holder nor the names of the contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


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
