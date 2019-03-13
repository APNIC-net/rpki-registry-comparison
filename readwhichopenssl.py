#!/usr/bin/env python3

import os
import sys
import subprocess
import ipaddress

OPENSSL='/usr/local/opt/openssl@1.1/bin/openssl'

def readcert(path):
    '''
    opens path, reads file, yields line-at-a-time
    '''
    CMD = OPENSSL + ' x509 -inform der -noout -text -in %s' % (path)
    ifp = subprocess.check_output(CMD, shell=True)
    for line in ifp.decode('utf-8').split('\n'):
        yield(line.rstrip())


# example main

def findINR(f, data):
    '''
    given an iterator over a cert, yield the tuple of (type, val) for INR
    '''
    for i in data:
        # skip the blanks
        if i == '':
            continue
        if 'Subject:' in i:
            #        Subject: CN = A91A73810000, serialNumber = 17E4E4989AB94E155BF1FD81CB585520CABFD337
            cn= i.split(',')[0].split()[-1]
        elif 'Autonomous System Numbers' in i:
            typ = 'ASN'
            for j in data:
                # end of ASN block
                if j == '':
                    break
                else:
                    yield(f, cn, typ, j.lstrip())
        elif 'sbgp-ipAddrBlock: critical' in i:
            for j in data:
                if 'IPv4' in j:
                    typ = 'IPv4'
                elif 'IPv6' in j:
                    typ = 'IPv6'
                elif j == '':
                    break
                else:
                    yield(f, cn, typ, j.lstrip())
        # skip rest
        else:
            continue

# example main
for (f,cn,t,i) in findINR(sys.argv[1], readcert(sys.argv[1])):
    if t == 'ASN' and '-' in i:
        x = list(map(int, (i.split('-'))))
        for j in range(x[0], x[1]+1):
            print(','.join((f,cn,t,str(j))))
    elif t == 'IPv4' and '-' in i:
        x = list(map(ipaddress.IPv4Address, (i.split('-'))))
        for j in list(ipaddress.summarize_address_range(x[0], x[1])):
            print(','.join((f,cn,t,str(j))))
    elif t == 'IPv6' and '-' in i:
        x = list(map(ipaddress.IPv6Address, (i.split('-'))))
        for j in list(ipaddress.summarize_address_range(x[0], x[1])):
            print(','.join((f,cn,t,str(j))))
    else:
        print(','.join((f,cn,t,i)))
