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

from syncster.crc import crc16
import struct, logging, serial

logger = logging.getLogger(__name__)

class ByteTagger(object):
    '''
    Helper object to allow a more expressive attribution of byte values <-> string.
    Initiate as:
    ```
        >>> foo = ByteTagger({'bar': 42, 'goo': 43})
        >>> foo.bar
        42
        >>> foo[42]
        'bar'
    ```

    Also implements keys() and items() to mimic a dict-like iteration interface.
    '''

    def __init__(self, bytemap):
        self._map = bytemap
        self._rev = { v:k for k,v in bytemap.items() }

    def __getitem__(self, code):
        return self._rev[code]

    def __getattr__(self, name):
        return self._map[name]

    def __len__(self):
        return len(self._map)

    def __iter__(self):
        for k, v in self._map.items():
            yield k

    def __str__(self):
        return str(self._map)

    def code(self, name):
        return self._map[name]

    def name(self, code):
        return self._rev[code]

    def names(self):
        return self.keys()

    def codes(self):
        return self._rev.keys()

    def keys(self):
        return self._map.keys()

    def items(self):
        return self._map.items()
    

ControlBytes = ByteTagger({
    'EOT':  0x0a,  # end-of-transmission
    'SOT':  0x0d,  # start-of-transmission    
    'XON':  0x11,  # flow control transmission-on
    'XOFF': 0x13,  # flow control transmission-off
    'ECC':  0x40,  # (no specific role, but needs to be escaped)
    'SOE':  0x5e,  # start-of-escape
})

Commands = ByteTagger({
    'NACK':   0x00, # sent by device if operation failed
    'CRCERR': 0x01, # sent by device for crc mismatch
    'ACK':    0x03, # send by device on successful write
    'READ':   0x04, # request data from register
    'WRITE':  0x05, # change state / write to register
    'DGRAM':  0x08, # received in response to a request
    'ECHO':   0x09, # send back supplied data (max 100 bytes)
    'REPLY':  0x10  # response to echo
})

Errors = ByteTagger({
    'SUCCESS':         0x0000,  # never received, usually successis marked by ACK
    'BUFFER_OVERFLOW': 0x0001, # internal error (bad, bad thing)
    'NOT_WRITABLE':    0x0002,
    'ARGSIZE_LOW':     0x0003,
    'ARGSIZE_HIGH':    0x0004,
    'INTERNAL_ERROR':  0x0005,
    'AUTHORIZATION_REQUIRED': 0x0006,
    'PROTERR_NOT_READABLE':   0x0007,
    'PROTERR_WRONG_ARGUMENT': 0x0008
})

class Message(object):
    '''
    This is the typical payload that goes between the PC and a Menlo Syncro.
    '''

    def __init_from_buffer(self, buffer):
        '''
        Receives a buffer and unpacks it into its individual components.
        If `escaped` is True, then the sequence is considered to need
        unescaping first.
	'''
        buf = unescape(buffer)
        
        ckours    = crc16(buf[:-2])
        cktheirs, = struct.unpack(">H", buf[-2:])

        if ckours != cktheirs:
            raise RuntimeError("CRC error on buffer: %r (%x != %x)" % (buf, ckours, cktheirs))

        self._dst, self._src, self._cmd = struct.unpack("BBB", buf[:3])
        self._data = buf[3:-2]
        self._buf = buf


    def __init_from_fields(self, src, dest, cmd, data):
        
        d = data
        if hasattr(data, 'encode'):
            d = data.encode('ascii')
        elif hasattr(data, '__len__'):
            d = bytearray(data)
            
        buffer = struct.pack('BBB', dest, src, cmd)
        buffer += d
        buffer += struct.pack('>H', crc16(buffer))
        
        self._buf = bytearray(escape(buffer))
        self._src = src
        self._dst = dest
        self._cmd = cmd
        self._data = d

    
    def __init__(self, buffer=None, src=None, dest=None, cmd=None, data=None, escaped=True):
        '''
        Constructs a RPB message in one of two ways:
           - either by accepting a buffer (containing a message including CRC)
           - or by accepting dest/src/data

        The fields of the message are accessible as properties:
            - `source`: the source device address (1 byte)
            - `destination`: the destination address (1 byte)
            - `data`: data payload (buffer of bytes, string, list of integers,
              ...)

        The CRC16 field is automatically calculated and appended to the buffer
        (if source/destination/data was specified), or checked against upon input.
        '''

        if buffer is not None:
            self.__init_from_buffer(buffer)
        else:
            self.__init_from_fields(src, dest, cmd, data)


    @property
    def buffer(self):
        return self._buf

    @property
    def source(self):
        return self._src

    @property
    def destination(self):
        return self._dst

    @property
    def command(self):
        return self._cmd

    @property
    def payload(self):
        return self._data


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        if self.command in [ Commands.READ, Commands.WRITE, Commands.ECHO ]:
            addr = "%.2x -> %.2x:" % (self.source, self.destination)
        else:
            addr = "%.2x <- %.2x:" % (self.destination, self.source)

        payload = " ".join([("%c"%x if x>32 and x<128 else "%.2x"%x)
                            for x in self.payload])
            
        return addr + \
            " %5s  " % ( Commands.name(self.command), ) + \
            payload + \
            " [%.2x%.2x]" % (self.buffer[-2], self.buffer[-1]) + \
            "  (" + " ".join(['%.2x' % x for x in self.buffer]) + ")"


class Device(object):

    '''
    This object wraps around a pyserial object and performs transmission
    of RBP messages. It is aware of Menlo devices peculiarities in the sense
    that it knows to what message what kind of reply to expect and does
    proper error processing (i.e. catching CRC or NACK errors and raising
    corresponding IOError exceptions).
    '''
    
    def __init__(self, port=None, **pyserial_kwargs):
        '''
        Opens the specified USB device for communication.
        `port` is the USB device name. The rest of the parameters
        are passed to the `Serial` initialisation.
        '''

        defaults = {
            'timeout':       3.0,       ## seconds -- should be enough.
            'write_timeout': 3.0,
            'inter_byte_timeout': 3.0,
            'baudrate': 115200,
            'parity':   serial.PARITY_NONE,
            'bytesize': serial.EIGHTBITS,
            'stopbits': serial.STOPBITS_ONE
        }

        if port is None:
            from os import environ as env
            try:
                port = env['SYNCSTER_PORT']
            except KeyError as e:
                print ("No port specified; tried to use one from $SYNCSTER_PORT, but that one is empty.")
                raise e

        for k in defaults.keys():
            if pyserial_kwargs.get(k, None) is None:
                pyserial_kwargs[k] = defaults[k]

        self.device = serial.Serial(port, **pyserial_kwargs)
        self.port   = port

    def sendMsg(self, msg):
        '''
        Sends either a buffer or a message to the device.
        '''

        if hasattr(msg, 'buffer'):
            buf = msg.buffer
        else:
            buf = msg

        sndbuf = bytearray([ControlBytes.SOT])+\
                 buf+\
                 bytearray([ControlBytes.EOT])

        #print ("sot>", " ".join(["%.2x"%x for x in bytearray([ControlBytes.SOT])]) )
        #print ("msg>", " ".join(["%.2x"%x for x in buf]))
        #print ("eot>", " ".join(["%.2x"%x for x in bytearray([ControlBytes.EOT])]) )
        #print (">>>", " ".join(["%.2x"%x for x in sndbuf]))

        nr = self.device.write(sndbuf)
        
        if nr < len(buf)+2:
            raise IOError("Write gone bad")

        self.device.flush()
                            

    def recvMsg(self):
        '''
        Receives exacly one response message from the device.
        Discards all bytes up until the first SOT byte first.
        Returns an Message() object.
        '''

        rcvbuf = bytearray()
        
        while True:
            b = self.device.read(size=1)
            if len(b) == 0:
                raise IOError("Timeout reading from %s" % self.port)
            rcvbuf += b
            if b[0] == ControlBytes.SOT:
                break
            else:
                #print ("<<< %.2x" % b[0])
                pass

            
        #print ("<<< (SOT)")

        buf = self.device.read_until(bytearray([ControlBytes.EOT]))
        if len(buf) == 0:
            raise IOError("Timeout reading from %s" % self.port)
        rcvbuf += buf

        #print ("<<<", " ".join(["%.2x"%x for x in rcvbuf]))

        return Message(buffer=buf[:-1])


    def req(self, msg, retryOnCrcErr=5):
        '''
        Sends one message, waits for response and interprets the response.
        If the message is a READ, the function returns the coresponding DGRAM message.
        If the message is a WRITE, the function checks for ACK/NACK and raises an IOError exception.
        If the message is an ECHO, the function returns one or more of the corresponding REPLY.
        '''

        while True:
            logger.debug("Request: %r" % msg)
            self.sendMsg(msg)
            r = self.recvMsg()
        
            if r.command in [ Commands.DGRAM, Commands.REPLY, Commands.ACK ]:
                return r

            if r.command == Commands.CRCERR:
                if retryOnCrcErr in [ None, False, 0 ]:
                    break
                retryOnCrcErr -= 1
                continue
            
            break

        # We'll land here if we have a proper error (CRCERR after
        # retransmit) or an NACK.
        raise IOError("Request failed: %r" % r)
    

def escape(buffer):
    '''
    Returns an escaped version of `buffer`, i.e. one in which each
    character from the control_bytes list has been replaced by the
    [SOE, char+64] sequence.
    '''
    buf = bytearray()
    for b in buffer:
        if b not in ControlBytes.codes():
            buf.append(b)
        else:
            buf.append(ControlBytes.SOE)
            buf.append(b+ControlBytes.ECC)

    return buf


def unescape(buffer):
    '''
    Returns an unescaped version of `buffer`, i.e. one where any
    escaped sequence of control bytes are replaced by their unescaped
    version.
    '''
    
    buf = bytearray()
    unmask = False
    
    for b in buffer:
        if unmask:
            buf.append(b-ControlBytes.ECC)
            unmask = False
        else:
            if b == ControlBytes.SOE:
                unmask = True
                continue
            buf.append(b)
            
    return buf


def test_byte_tagger():

    assert len(Errors.codes()) == len(Errors.names())
    
    for n in Errors.names():
        assert isinstance (n, str)

    assert Errors.SUCCESS == 0


def test_escape():
    # Testing escaping / unescaping of bytes.
    regular = [ bytearray('abcde', encoding='ascii') ]
    goofy = [ bytearray([c for c in ControlBytes.codes()]) ]

    for b in regular:
        assert b == escape(b)
        assert b == unescape(b)
        assert b == escape(unescape(b))

    for g in goofy:
        b = escape(g)
        for n,c in ControlBytes.items():
            if n != 'SOE':
                assert c not in b
        assert ControlBytes.SOE in b
        assert g != b
        assert g == unescape(b)

        
def test_unpack():
    # Testing unpacking of src/dest/data from buffer
    msg = [ bytearray([0x42, 0x5e, 0x51, 0x04, 0x0f, 0x06, 0x94, 0xc0]),
            bytearray([0x5e, 0x51, 0x42, 0x08, 0x0f, 0x0e, 0x0c, 0x09, 0x77, 0xcc ]) ]

    b = [Message(m) for m in msg]

    assert b[0].destination == 0x42
    assert b[0].source  == 0x11
    assert b[0].command == Commands.READ
    assert b[0].payload == bytearray([0x0f, 0x06])
    assert b[1].destination == b[0].source
    assert b[1].command == Commands.DGRAM

    for x,y in zip(b,msg):
        assert len(x.payload) != 0

    
def test_pack():
    msg = [ bytearray([0x42, 0x5e, 0x51, 0x04, 0x0f, 0x06, 0x94, 0xc0]),
            bytearray([0x5e, 0x51, 0x42, 0x08, 0x0f, 0x0e, 0x0c, 0x09, 0x77, 0xcc ]) ]

    for m in msg:
        tmp1 = Message(m)
        tmp2 = Message(src=tmp1.source, dest=tmp1.destination,
                       cmd=tmp1.command, data=tmp1.payload)

        assert tmp2.buffer == m

        
def test_echo():
    #return   #### TEST DISABLED\
    dev = Device()
    m = Message(src=0x11, dest=0xff, cmd=Commands.ECHO, data='hello')
    print(m)
    r = dev.req(m)
    print(r)
    assert r.command == Commands.REPLY

    
def test_readreg():
    # Trying to read a port -- this is literally the documentation example.
    
    dev = Device()
    m = Message(src=0x11, dest=0x42, cmd=Commands.READ, data=[0x0f, 0x06])
    print(m)
    
    r = dev.req(m)
    print(r)

    assert r.command == Commands.DGRAM
