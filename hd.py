#!/usr/bin/env python
#

import socket
import struct
import sys


def address_to_bytes(address):
    host, port = address
    try:
        host = socket.gethostbyname(host)
    except (socket.gaierror, socket.error):
        raise ValueError, "invalid host"
    try:
        port = int(port)
    except ValueError:
        raise ValueError, "invalid port"
    b = socket.inet_aton(host)
    b += struct.pack("H", port)
    return b


def main():
    port = 4653
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        pass

    sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockfd.bind(("", port))
    print "listening on *:%d (udp)" % port

    poolqueue = {}
    while True:
        data, addr = sockfd.recvfrom(32)
        print "connection from %s:%d" % addr

        pool = data.strip()
        sockfd.sendto("ok " + pool, addr)
        data, addr = sockfd.recvfrom(2)
        if data != "ok":
            continue

        print "request received for pool:", pool

        try:
            a, b = poolqueue[pool], addr
            sockfd.sendto(address_to_bytes(a), b)
            sockfd.sendto(address_to_bytes(b), a)
            print "linked", pool
            del poolqueue[pool]
        except KeyError:
            poolqueue[pool] = addr


if __name__ == "__main__":
    main()
