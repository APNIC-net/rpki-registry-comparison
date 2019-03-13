#! /usr/bin/env python3

import sys
import getopt

from io import BytesIO

# be able to get data off the web
import urllib.request

inverse = 0

# get all the Delegated class public functions
from Delegated import Delegated
DELEGATED_SOURCE = 'http://labs.apnic.net/delegated-nro-extended'


# main is the go.. but we run in __main__
def main(argv):                         

    global debug, delegf, inverse, fd, field, sep, tag

    debug = 0        # by default not debugging

    delegf = None

    fd = sys.stdin

    sep = None

    tag = None

    # initialize a radix tree instance to play with
    deleg = Delegated()

    # args processing.
    try:                                
        opts, args = getopt.getopt(argv, "vhd:Ds:n:t:", ["inverse", "help", "delegated", "Debug", "separator", "number", "tag"])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt == '-v':
            inverse = 1
            if (debug == 1):
                print("inverse match")

        elif opt == '-t':
            tag = arg.split(',')
            if (debug == 1):
                print("tag to append ", tag)
        elif opt == '-D':
            debug = 1
            print("debug enabled")
        elif opt == '-d':
            delegf = arg   
            try:
                fd = open(delegf,'r')
            except:
                print("unable to open %s for reading", delegf)
                sys.exit()

            if (debug == 1):
                print("delegated prefixes from ", delegf)
        elif opt == '-n':
            field = int(arg)   
            if (debug == 1):
                print("field to select on is", field)

        elif opt == '-s':
            sep = arg   
            if (debug == 1):
                print("field separator is", sep)

    if debug:
        sys.stderr.write('delegated file load start\n')
        sys.stderr.flush()

    if tag == None or len(tag) == 0:
        tag=['cc','orgid']

    if delegf == None:
        # get data from the URL
        try:
            req = urllib.request.Request(DELEGATED_SOURCE)
            response = urllib.request.urlopen(req)
        except IOError as e:
            sys.stderr.write('failed to fetch %s: %s\n' % (DELEGATED_SOURCE, e))
            sys.exit(1)

        # we can now create the IO chain to handle the .gz input
        fd = BytesIO(response.read())

    # otherwise, fd was set when delegf was read or is sys.stdin.

    # parse on field|field|field separated data by default

    try:
        deleg.delegatedRadix(fd)
    except Exception as e:
        sys.stderr.write("Delegated.delegatedRadix() %s\n" % (str(e)))
        fd.close()
        sys.exit(1)

    # we're done loading the pfx tree.
    fd.close()

    for line in sys.stdin:
        line = line[:-1]    # chomp

        # first the skips.

        # skip empties and comments and summary lines
        if not line.strip():
            continue
        if line.startswith('#'):
            continue

        # split. use list comprehension to trim lwsp around words
        # separated by the chosen separator (default is lwsp)
        wrdz = [i.strip() for i in line.split(sep)]

        mat = None

        try:

            mat = deleg.rtree.search_best(wrdz[field])
            if (debug == 1):
                sys.stderr.write("rtree.search_best mat(%s)\n" % (wrdz[field]))
        except Exception as e:
            if (debug == 1):
                sys.stderr.write("rtree.search_best mat(%s): %s\n" % (wrdz[field], str(e)))
                continue

        from operator import itemgetter

        if (mat is not None):
            if inverse > 0:
                continue
            else:
                if len(tag) > 0:
                    print(sep.join((line,sep.join(itemgetter(*tag)(mat.data)))))
                else:
                    print(line)
        else:
            if inverse > 0:
                print(line)
            else:
                continue
            if (debug == 1):
                sys.stderr.write("rtree.search_best mat(%s): None\n" % (wrdz[field]))

    sys.exit()


def usage():
    print('Usage: ' + sys.argv[0] + ''' -v -d <file> -h -D -s <str> -n <num>
    -v inVerse: like grep -v to exclude thing
    -h print this display
    -D debug mode 
    -d delegated-prefix-file
    -s sep # character to separate input fields on
    -t tag # data from delegated file to match on  (yield({'rir':v[0], 'cc':v[1], 'type':v[2], 'prefix':v[3], 'len':len, 'date':v[5], 'status':v[6]}))
    -n num # field to read on''')

# the real main

if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        usage()
        sys.exit(2)

    main(sys.argv[1:])
