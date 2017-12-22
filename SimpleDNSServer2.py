#!/usr/bin/env python

import sys
import socket
import thread
import re

# DNSQuery class from http://code.activestate.com/recipes/491264-mini-fake-dns-server/
class DNSQuery:
    def __init__(self, data):
        self.data=data
        self.domain=''

        tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
        if tipo == 0:                     # Standard query
            ini=12
            lon=ord(data[ini])
            while lon != 0:
                self.domain+=data[ini+1:ini+lon+1]+'.'
                ini+=lon+1
                lon=ord(data[ini])

    def respuesta(self, ip):
        packet=''
        if self.domain:
            packet+=self.data[:2] + "\x81\x80"
            packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
            packet+=self.data[12:]                                         # Original Domain Name Question
            packet+='\xc0\x0c'                                             # Pointer to domain name
            packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
            packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
        return packet


def usage():
    print "Usage: SimpleDNSServer [filter string]"
    sys.exit(1)

def query_and_send_back_ip(data, addr):
    try:
        p=DNSQuery(data)
        if sys.argv[1] in p.domain:
            print 'Request domain: %s' % p.domain
            ip = '127.0.0.1'
            udps.sendto(p.respuesta(ip), addr)
            print 'Request: %s -> %s' % (p.domain, ip)
    except Exception, e:
        print 'query for:%s error:%s' % (p.domain, e)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    try:
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.bind(('',53))
    except Exception, e:
        print "Failed to create socket on UDP port 53:", e
        sys.exit(1)

    print 'SimpleDNSServer listening on 0.0.0.0:53'

    try:
        while 1:
            data, addr = udps.recvfrom(1024)
            query_and_send_back_ip(data, addr)
    except KeyboardInterrupt:
        print '\n^C, Exit!'
    except Exception, e:
        print '\nError: %s' % e
    finally:
        udps.close()