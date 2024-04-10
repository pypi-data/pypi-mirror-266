Synster -- Python API for Menlo Syncro box
==========================================

Dependencies
------------

Needs:
  - python3-pyserial
  - python3-

Quick'n Dirty Snippets
----------------------

Try this:

```
>>> from rbp import Message, Device, ControlBytes, Errors, Commands
>>> dev = Device("/dev/ttyUSB0")
>>> m = Message(src=0x0, dest=0xff, cmd=Commands.ECHO, data='hi!')
>>> r = dev.req(m)
>>> print(r)
```

Test like this, if you already have a Menlo Syncro attached:
```
$ export SYNCSTER_PORT=/dev/ttyUSB0
$ cd syncster/syncster
$ pytest-3 -s rbp.py
```

