import math
import sys
from radix import Radix

def _delegatedSwitcher(asnfunc, ipfunc, genitem):
    '''
    given item from genitem, if item has 'asn' as a key, call asnfunc(item)
    otherwise, if it has 'ipv4' or 'ipv6' then call ipfunc(item)
    '''
    for i in genitem:
        if i['type'] == 'asn':
            asnfunc(i)
        elif i['type'] in ['ipv4', 'ipv6']:
            ipfunc(i)


# private generator to yield the specific fields we want
def _delegatedFieldSelector(fields, genitem):
    '''
    selects fields (dict keys) from items from genitem, which is from the dict yield() its called over
    '''
    for item in genitem:
        ret={}
        for i in fields:
            if i in item:
                ret[i] = item[i]
        yield(ret)

# private function by idiom, but actually its just specified in Delegated. 
def _cnt2pfx(hc):
    ''' given a hostcount, return the prefix equivalent. 
        fix strs to int() and avoid float promotion 
        via the math.log() function.  hc for h(ost) c(ount)
    '''

    # for the log() function

    return(32-int(math.log(int(hc),2)))

# not very private, intimate generator to filter the delegated Input
def _filterDelegated(genline):
    for l in genline:
        line = l.decode('utf-8')

        # a form of chomp()
        line = line.rstrip()

        # skip empties and comments and summary lines
        if not line.strip(): 
            continue
        elif line.startswith('#'):
            continue
        elif 'summary' in line:
            continue
        # skip version line. starts with digit.
        elif line[0].isdigit():
            continue
        # skip ietf/iana/Not_in_stats lines. 
        elif 'ietf' in line:
            continue
        elif 'iana' in line:
            continue
        elif 'Not_in' in line:
            continue
        elif 'available' in line:
            continue
        elif 'reserved' in line:
            continue
        yield(line)


# private function to read the delegated file into yield() returns of a dict
def _readDelegated(fd):
    '''        
    Reads well-formed 'stats' format lines. A good line is

    apnic|JP|ipv4|3.18.0.0|4194304|19890221|allocated
    apnic|CN|ipv4|1.0.32.0|8192|20110412|assigned|A92319D5|e-stats
        0  1    2        3    4        5        6        [7    8]
      rir cc type  prefix cnt/pfx   date    status [orgid source]

    in the case of v4, field 4 needs to be 'converted'
    from hostcount to prefixlen.
    '''

    for line in _filterDelegated(fd):
        # get words. by default, split() operates on LWSP
        try:
            v = line.split('|')
        except Exception as e:
            sys.stderr.write("Delegated().readDelegated().split(%s): %s\n" % (line, str(e)))
            continue

        # its either v4 or v6. 
        # v6 len IS a prefix. v4 convert.
        if (v[2] == "ipv4"):
            try:
                len=_cnt2pfx(v[4])
            except Exception as e:
                sys.stderr.write("Delegated().readDelegated()._cnt2pfx(%s): %s\n" % (v[4], str(e)))
                continue
        else:
            len = int(v[4])

        # asn emit one per len value until exhausted
        if 'asn' in line:
            basn = int(v[3])
            while len > 0:
                len -= 1
                yield({'rir':v[0], 'cc':v[1], 'type':v[2], 'prefix':str(basn), 'len':1, 'date':v[5], 'status':v[6], 'orgid':v[7], 'source':v[8]})
                basn += 1
        else:
            yield({'rir':v[0], 'cc':v[1], 'type':v[2], 'prefix':v[3], 'len':len, 'date':v[5], 'status':v[6], 'orgid':v[7], 'source':v[8]})

    # implicit return lies in the yield()


class    Delegated: 

    # for radix tree data structure

    # method to instantiate a new instance of a radix trie and an ASN dict to play in
    def __init__(self):
        # initialize a radix tree
        self.rtree = Radix()
        # initialize an asn dict
        self.asn = {}


    # private function which consumes a generator
    # not very private Method to add one ASN to the dict
    def _asnfunc(self, item):
        self.asn[item['prefix']] = item

    # not very private Method to add one ASN to the dict
    def _ipfunc(self, item):
        # save in the radix tree under 'prefix/len' for the value
        key = '%s/%s' % (item['prefix'], item['len'])

        try:
               # set the radix instances up keyed on prefix/len.
               rn = self.rtree.add(key)
        except Exception as e:
               sys.stderr.write("Delegated.delegatedRadix().rtree.add(%s): %s\n" % (key, str(e)))
               sys.exit(1)

        # dict copy because radix trie points to magic data ???????
        for k,v in item.items():
               rn.data[k] = v
        # and add a counter
        rn.data['cnt'] = 0


    # Method which just mutates its self to set value into .rtree and .asn
    def delegatedRadix(self, fd):
        '''
        given a file, read it as a delegated file into the radix tree.
        '''

        import sys

        _delegatedSwitcher(self._asnfunc, self._ipfunc, _delegatedFieldSelector(['type', 'prefix', 'len', 'cc', 'orgid', 'date', 'rir', 'source', 'status'], _readDelegated(fd)))


if __name__ == "__main__":
    import sys

    x = Delegated()
    sys.exit(0)

