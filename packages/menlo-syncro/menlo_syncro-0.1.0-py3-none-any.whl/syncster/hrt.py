#!/usr/bin/python3

#
#        Syncster Library for terminal access to Menlo Syncro synchronizers.
#        Copyright (C) 2022 Florin Boariu.
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from syncster import rbp
import logging, struct

logger = logging.getLogger(__name__)

'''
This implements structures and definitions for handling the
Hierarchical Register Tree (HRT). It starts off with the minimal
device tree as defined by the Menlo documentation, and offers
ways to easily extend the register definitions.
'''


'''
This is a list of types known to HRT, by name, and their
respective binary data format. Note that possibly not all types
have been transfered to Python code -- complete as necessary.
They are documented in Menlo's "HRT Protocol Specification",
e.g. v0.2.7 page 8 ff.

This dictionary is designed to present the information in an easily machine-readable
and interpretable way. The key is the human-readanble label, which is mostly the same 
as in the official Menlo documentation. The value is a dictionary itself with the following
keys:

       - "label": human-readable name for the type

       - "format": Python struct formatting string for parsing/writing. In the
         most cases this is simply a string with format magic characters; but sometimes
         the formatting depends on the data itself (e.g. when parsing variable-length
         data). For this, "format" is also accepted to be a callable, e.g. a lambda.
         If it is, it is called with one single parameter -- the data itself -- and
         the return value is interpreted as a struct unpacking string.

       - "format_keys": optional; if it exists, in its most simple form it's a list of
         strings (keys) that designates the name(s) of the data field(s) represented in
         format. Only really makes sense for formats that are structures (i.e. composed
         of multiple fields). For instance: `[ 'type', 'label', 'rw']`.
         Optionally, this can also be a dictionary, in which case
         the keys of the "format_keys" dictionary are the key names of the data fields,
         and the values of the "format_keys" dictionary are casting/transformation callables
         for data processing, e.g.: `{ 'type': int,
         'label': lambda s: s.decode('ascii'), 'rw': int }`. The latter example would 
         transform the 2nd parameter ("label") into a string on the fly, after having parsed
         it into a bytearray first.

       - "units": optional; if it exists, it is a hint as to the units of the data
         (usually only useful to the end user and/or for displaying purposes).
'''

RegisterDataTypes = {
   
    0x01: { "label": "NONE", "format": None },
    0x02: { "label": "NODE", "format": None },

    # Docs say this is supposed to be one U8 value, but my device returns 3 bytes, e.g. (2, 1, 1)
    0x03: { "label": "REGVERS", "format": lambda b: "%dB" % len(b) },
    
    0x04: { "label": "SUBREGS", "format": lambda b: "%dB" % len(b) },

    # String parameter is sent 0-terminated, but we'll parse it without the 0.    
    0x05: { "label": "REGDEF", "format": lambda b: "B%dsxB" % (len(b)-3),
            "format_keys": { "type": int,
                             "label": lambda s: s.decode('ascii'),
                             "access": lambda s: ["", "rw", "r", "w"][s] } },
    
    0x07: { "label": "ADDRESS", "format": "B" },
    0x08: { "label": "TYPE", "format": "<H" },

    0x09: { "label": "SERS", "format": "<BBH", "format_keys": [ "day", "month", "year" ] },

    0x0a: { "label": "REMOTE_SERVICEMODE", "format": "B" },
    
    0x0d: { "label": "TSTAMP", "format": "<LH", "format_keys": [ "sec", "msec" ] },
    
    0x0f: { "label": "DEVID", "format": lambda b: "%dsx" % (len(b)-1) },

    # format: VERS
    0x10: { "label": "VERS", "format": "BBBB", "format_keys": [ "build", "patch", "minor", "major" ] },

    #0x20: { "label": "EDIP_BMP", "format": lambda b: "%dB" % len(b) },
    #0x21: { "label": "EDIP_FW", "format": lambda b: "%dB" % len(b) },

    0x30: { "label": "REMODE_EDIP", "format": "B" },
    0x31: { "label": "REMODE_AMP", "format": "B" },
    0x32: { "label": "REMODE_SEED", "format": "B" },
    0x33: { "label": "REMODE_SPI", "format": lambda b: "%dB" % len(b) },
    
    0x50: { "label": "SAVESETTINGS", "format": "B" },
    0x51: { "label": "U16_mA", "format": "<H", "units": "mA" },
    0x52: { "label": "CALIB_DAC", "format": "<llllHH" },
    0x53: { "label": "CALIB_ADC", "format": "<llll" },
    0x54: { "label": "S32_mV", "format": "<l", "units": "mV" },
    0x55: { "label": "U8_enum", "format": "B" },
    0x56: { "label": "U8_bool", "format": "B" },

    0x57: { "label": "S32_mV", "format": "<l", "units": "mV" },
    0x58: { "label": "S32",    "format": "<l", "units": "steps" },
    0x59: { "label": "S32_mC", "format": "<l", "units": "m°C" },
    0x5a: { "label": "S32_uC", "format": "<l", "units": "μ°C" },
    
    0x5b: { "label": "U32_Hz", "format": "<l",  "units": "Hz" },
    0x5b: { "label": "U32_mHz", "format": "<l", "units": "mHz" },
    0x5b: { "label": "U32_kHz", "format": "<l", "units": "kHz" },
    0x5b: { "label": "U32_mW", "format": "<l",  "units": "mW" },
    
    0x5f: { "label": "S32_uV", "format": "<l", "units": "uV" },

    0x60: { "label": "U32_us", "format": "<l", "units": "us" },

    0x61: { "label": "S32_mA", "format": "<l",   "units": "mA" },
    0x62: { "label": "S32_mW_K", "format": "<l", "units": "mW/K" },
    0x63: { "label": "S32_mJ_K", "format": "<l", "units": "mJ/K" },
    
    0x81: { "label": "U16", "format": "<H" },

    0xae: { "label": "SYNCHRO_TRACKLOG",
            "format": "<llll",
            "format_keys": [ "lb_out", "t1_pos", "lb_in", "t2_pos" ] },

    # This is from the main documentation (does this contain one or several such lines?)
    #0xe4: { "label": "LOGHIST", "format": lambda b: ("<L>HBB>L>L" * (len(b)/16)),
    #        #"format_keys": [ "sec", "msec", "context", "event", "val", "ref" ] },
    #       }

    # This is from the Syncro RRE documentation, apparently it contains
    # up to 50 such entries. Strategy here would be to auto-sense that the
    # buffer size is a multiple of the format size and run struct.iter_unpack(),
    # then return an array of log entries.
    0xe4: { "format": "<LlBBBBBllHH",
            "format_keys": [ "sec", "msec", "remain",
                             "level", "context", "subcontext1", "subcontext2",
                             "msgid", "line", "val", "ref" ] },
           
}

'''
HR Tree information for register introspection (i.e. information
about further register layout).
'''
IntrospectionTree = {
    "RegVers":     { "addr": b'\xfd', "type": 0x03, "access": "r" },
    "Subregs":     { "addr": b'\xfe', "type": 0x04, "access": "r" },
    "RegDef":      { "addr": b'\xff', "type": 0x05, "access": "r" }
}

MinimalDeviceTree = {
    "Addr":    { "addr": b'\x01', "type": 0x07, "access": "rw" },
    "Type":    { "addr": b'\x02', "type": 0x08, "access": "r"  },
    "Serial":  { "addr": b'\x03', "type": 0x09, "access": "rw" },
    "SaveSet": { "addr": b'\x04', "type": 0x50, "access":  "w" },
    "TStamp":  { "addr": b'\x08', "type": 0x0d, "access": "r"  },
    "Uptime":  { "addr": b'\x11', "type": 0x0d, "access": "r"  },
    "Id":      { "addr": b'\x0a', "type": 0x0f, "access": "r"  },
    "HwVer":   { "addr": b'\x0b', "type": 0x10, "access": "r"  },
    "FwVer":   { "addr": b'\x0c', "type": 0x10, "access": "r"  },
}


class RegisterAccess:
    '''
    Encapsulates HRT access procedures. Uses `syncster.rbp.Message` and `syncster.rbp.Device`
    to convey access to a specific register according to its specified formats.

    The registers are defined in a Python dicitionary format (see `MinimalTree` for instance).
    '''

    def __init__(self, dev, src=0xff, dst=0xff,
                 addr_prefix=None, addr_suffix=None,
                 **rspec):
        '''
        Initialises an Access class for a specific device connection with
        a specific tree entry (i.e. a single register).
        Parameters:

          - `dev`: the RBP device to use

          - `src`: ID of the requesting device (i.e. "us"), defaults to 0xff

          - `dst`: ID of the device we want to talk to (i.e. "peer"), defaults to 0xff

          - `addr_prefix`: if specified, this byte array will be put in front of the
            "addr" for every request. It's an easy and convenient way of defining
            access to similar types of registers that differ only in a prefix.

          - `addr_suffix`: similar to `addr_prefix`, just being appended to the
            address.

          - `rspec`: register specification dictionary; must contain at least the key
            "addr", and should also contain "access" and "format_keys".
            It also must contain either "format" (a string or callable which describes
            how to unpack the data using `struct.unpack()`) or "type" (a numerical
            key of `RegisterDataTypes`)

        '''
        self.dev = dev
        self.src = src
        self.dst = dst
        self.access = rspec.get('access', 'r')
        
        self.addr = \
            bytearray(addr_prefix or b'') + \
            bytearray(rspec['addr']) + \
            bytearray(addr_suffix or b'')
        
        if "format" in rspec:
            fmt_dict = rspec
        else:
            try:
                fmt_dict = RegisterDataTypes[rspec['type']]
            except KeyError:
                logger.warning("Missing type definition for 0x%.2x -- decoding as byte array" % rspec['type'])
                fmt_dict = { 'format': lambda b: '%dB' % len(b) }
            
        self.fmt = fmt_dict['format']
        self.fmt_keys = fmt_dict.get('format_keys', None)


    def _read(self, addr=None):

        if 'r' not in self.access:
            raise RuntimeError("Register %x cannot be read (access: %s)"
                               % (self.addr, self.access))
        
        # Reading operation only.
        response = self.dev.req(rbp.Message(src=self.src, dest=self.dst,
                                            cmd=rbp.Commands.READ, data=self.addr))

        # First byte is the register (address) prefix, the rest
        # is actual register readout data.
        reg = response.payload[:1]
        dat = response.payload[1:]
        #reg = response.payload[:len(self.addr)]
        #dat = response.payload[len(self.addr):]

        # format is either an unpack string, or a callable generating an unpack string.
        fmt = self.fmt(dat) if hasattr(self.fmt, "__call__") else self.fmt

        logger.debug("Response: %r" % response)
        logger.debug("Format: %s" % fmt)

        #print ()
        #print ("Message:", response)
        #print ("Register:", reg)
        #print ("Datagram:", dat)
        #print ("Format:", fmt)

        tmp_data = struct.iter_unpack(fmt, dat)
        logger.debug ("Unpack:", tmp_data)

        # apply field naming -- note that we treat all data as if it
        # had been iter-inp
        if self.fmt_keys is not None:
            data = []
            for dt in tmp_data:
                # if fmt_keys is a dictionary, the 'value' is in fact a translator.                
                if isinstance(self.fmt_keys, dict):
                    data.append( { k:v(d) for (k,v),d in zip(self.fmt_keys.items(), dt) } )
                else:
                    data.append( { k:v for k,v in zip(self.fmt_keys, dt) } )
        else:
            data = [x for x in tmp_data]
                        
        if struct.calcsize(fmt) == len(dat):
            # reduce to simple item if iter_unpack() wasn't necessary
            data = data[0]

        # reduce again to only blank element if unpacking only resulted in one single item
        if len(data)==1:
            data = data[0]

        return data


    def _write_values(self, *args):
        
        if 'w' not in self.access:
            raise RuntimeError(f"Register {self.addr} cannot be modified (access: '{self.access}')")

        # format is either an unpack string, or a callable generating an unpack string.
        if hasattr(self.fmt, "__call__"):
            raise RuntimeError(f'Cannot pack data using a callable format spec')
        
        data = struct.pack(self.fmt, *args)
        
        response = self.dev.req(rbp.Message(src=self.src, dest=self.dst,
                                            cmd=rbp.Commands.WRITE,
                                            data=self.addr+data))

        logger.debug("Response: %r" % response)

        return response

        
    def __call__(self, *args, **kw):
        '''
        Reads/writes data to register, or, optionally, to/from named register fields.
        FIXME: how do we access indivitual fields by name only, without accessing other
               fields of a specific register?...
        '''

        if len(args) == 0 and len(kw) == 0:
            return self._read()

        elif len(args) > 0:
            if len(kw) > 0:
                raise RuntimeError(f'You may write values into registers either '
                                   f'by value or by name, not both')
            # Writing operation, by value(s)
            self._write_values(*args)
            
        else:
            if len(args) > 0:
                raise RuntimeError(f'You may write values into registers either '
                                   f'by value or by name, not both')
            # Writing operation, by name(s)
            raise RuntimeError('Writing by name not implemented')
            pass        


class NodeAccess:
    '''
    Offers easy Python-esque access to HRT registers by name, as members of
    a class (this class). Each HRT node may contain two types of entries:
    "subnodes" and "registers".

    A register is an endpoint, essentially containing useful data, that can
    be accessed using the RBP commands `READ` and `WRITE`, and which may receive
    replies in the form of `ACK`, `NACK`, `DGRAM` or others.

    Each node has at least 3 registers. They are specified in `IntrospectionTree`:
    
      - `RegVers`: a register containing a data tuple specifying the register
        version implemented within the device;

      - `Subregs`: a register containg an array of integers (bytes) with the
        IDs of all the node entries

      - `RegDefs`: a register containing definitions (name, data type, access type)
        for each of the registers in `Subregs`.
     
    '''
    def __init__(self, dev=None, node=None, tree=None, recurse=1, **raParams):
        '''  Initializes a HRT node access class based on device  and tree information.
        
        The tree information is analogous to `IntrospectionTree`.
        It uses `hrt.RegisterAccess` under the hood. `raParams` are
        passed on as parameters for `RegisterAccess` calls and may contain        
        supplementary settings as `addr_prefix` or similar.

        Args:
        
            dev: a `rbp.Device` object

            node: a list of integers (node address). If the list is empty, the root
              is accessed.

            tree: a dictionary of the expected entries on the node to access. If this
              is `None`, the node is assumed to contain at least the `hrt.IntrospectionTree`
              items (typically true only for a root node) and the complete list is
              obtained by introspection using those registers.
        '''

        if recurse < 0:
            raise RuntimeError("Recursion too deep")
        
        self._dev = dev or rbp.Device()

        # Node is supposed to be a sequence of bytes. For convenience, we accept
        # single integer values, but convert them to sequences as soon as possible.
        if node is None:
            self._node = []
        else:
            self._node = node if hasattr(node, "__len__") else [node]
            logger.debug("New access for node: %r" % (self._node,))

        # Rely on 'node' and enquire a tree layout from the device itself.
        if tree is not None:
            _tree = tree
        else:
            _tree = ls_node(dev=self._dev, node=self._node)
        
        self._regs = { }
        self._subs = { }

        # need to rebuild tree because we might have to mangle keys
        self._tree = { }
        
        for k,v in _tree.items():

            # Key name mangling -- the device node naming doesn't follow Python syntax,
            # may contain white spaces etc. We need to adjust the key. We remove everything
            # non-alpahnumeric, and turn stuff to camel case. Hope this does it.
            key = ''.join( ''.join(j for j in i if j.isalnum())[:1].upper()+
                           ''.join(j for j in i if j.isalnum())[1:] \
                          for i in k.split(' '))
            key_orig = key

            # As a precaution, make sure 'key' doesn't already exist. If it does,
            # make it unique.
            key_cnt = 2
            while (key in self._subs) or (key in self._regs):
                key = "%s%d" % (key_orig, key_cnt)
                key_cnt += 1

            self._tree[key] = _tree[k]

            logger.debug("New key: %s" % key)
            
            if v['access'] == '':
                # For subregisters, we do lazy-loading only to avoid recursion
                # within the device introspection data itself.
                self._subs[key] = v
            else:
                self._regs[key] = RegisterAccess(self._dev, **raParams, **v)

        self._subcache = {}

        
    def ls(self, f=lambda i: True):
        return {k:v for k,v in filter(f,self._tree.items())}

    
    def __dir__(self):
        return [i for i in self._regs.keys()] + \
            [i for i in self._subs.keys()]

    
    def __getattr__(self, key):
        r = self._regs.get(key, None)
        if r is not None:
            return r

        s = self._subs.get(key, None)
        if s is None:
            raise AttributeError(key)

        # s['addr'] already contains the full address; otherwise we'd have
        # to prepend the current self._node to it.
        return self._subcache.get(key) or \
            self._subcache.setdefault(key, NodeAccess(dev=self._dev, node=s['addr']))


def test_nac_simple():
    # simple test for node access (just access of tree data)
    
    n = NodeAccess(tree=IntrospectionTree)
    assert sorted(dir(n)) == sorted(IntrospectionTree.keys())
    s = n.Subregs()
    assert len(s) > 0
    print ("Subregisters:", s)


def test_nac_introspection():
    # Testing automatic introspeciton using NodeAccess

    n = NodeAccess()
    print("Root Registers:", dir(n))

    assert len(dir(n)) > 3
    for i in ["Subregs", "RegDef", "RegVers"]:
        assert i in dir(n)

    for s in n.Subregs():
        sintro = NodeAccess(tree=IntrospectionTree, addr_suffix=[s])
        if sintro.RegDef()['type'] == 2:
            snode = NodeAccess(node=s)
            print ("Sub:", s, "info:", sintro.RegDef(), "fields:", dir(snode))

    print ("Device ID:", n.DEV.ID())
    assert len(n.DEV.ID()) > 0
    


def ls_node(dev=None, node=None):
    '''
    Uses introspection registers to read out information about
    a specific node. Returns a HRT tree dictionary, see `IntrospectionTree`
    for a formatting example and documentation.
    '''

    suffix = node or []
    base = NodeAccess(dev, tree=IntrospectionTree, addr_suffix=suffix)
    tree = {}
    
    for r in base.Subregs():
        sub = NodeAccess(dev, tree=IntrospectionTree, addr_suffix=(node or []) + [r])
        info = sub.RegDef()
        info['addr'] = (node or []) + [r]
        tree[info['label']] = info

    return tree


def test_ls_node():
    tree = ls_node()
    
    from pprint import pprint
    print("Root tree:")
    pprint(tree)
    
    assert len(tree) > 0

    assert 'RegVers' in tree
    assert 'Subregs' in tree
    assert 'RegDef' in tree

    ls_node(node=[0x01])
    

def debug_ls_node(node=None, name='root'):
    # Debugging version of ls_node -- lists all registers of a specific node.
    # For productive purposes this has long been relaced by ls_node(), but
    # we still keep this one around because it's more specific and good for
    # experimenting and documentation purposes.
    #
    # Do not use in production, might disappear!
    
    # Nested register access (i.e. registers with address larger than 1 byte)
    print()

    # This is the DEV register number for Syncro RRE.
    # This will essentially list all subregisters.
    devRegister = [node] if node is not None else []
    
    dev = rbp.Device()
    reg = RegisterAccess(dev, addr_suffix=devRegister, **IntrospectionTree['Subregs'])
    
    registers = reg()
    
    assert len(registers) > 1
    #assert 255 in registers

    print ("HRT Registers for %s[%.2x]: %r" % (name, (node if node is not None else 0), registers))

    for r in registers:
        regInfo = RegisterAccess(dev, addr_suffix=bytearray(devRegister + [r]), **IntrospectionTree['RegDef'])
        ri = regInfo()
        
        print ("Register %.2x: %r" % (r, ri))

        assert len(ri['label']) > 0
        assert ri['access'] in ["", "r", "w", "rw"]

        ## type 2 is NODE, which is neither readable nor writable        
        if ri['type'] == 2:
            assert ri['access'] == ""
        else:
            assert ri['access'] in ["r", "w", "rw"]

        if r == 0x0a:
            devId = RegisterAccess(dev, addr_prefix=devRegister, **MinimalDeviceTree['Id'])
            print ("  + Device ID:", devId())


def test_registeraccess():
    debug_ls_node(None)
