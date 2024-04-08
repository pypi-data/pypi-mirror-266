# lmwsip
## Introduction

lmwsip is a python library for the lmw sip protocol.

## Package

The lmwsip package contains the class LmwSip to connect to the
[LMW](https://waterberichtgeving.rws.nl/water-en-weer/metingen/lmw-info)
meetnet using de SIP protocol. The library contains documentation
how to use it.

## Installing

Just install the package with 'pip':

``` 
pip install lmwsip
``` 

## Examples

### Username password

All examples contain "USER", "PASS".
These values should be replaced by real credentials.
Otherwise the connection fails.

### Use send (low level)

``` python
from lmwsip import LmwSip

sip = LmwSip(ssl=True, host="sip-lmw.rws.nl", port=443)
sip.send("LI user,pass\r")
print("< [%s]" % (sip.recv().strip('\r')))
sip.send("TI LMW\r")
print("< [%s]" % (sip.recv().strip('\r')))
sip.send("LO\r")
print("< [%s]" % (sip.recv().strip('\r')))
```

#### Use value

``` python
from lmwsip import LmwSip
sip = LmwSip("USER", "PASS")
print(sip.ti())
print(sip.value("WN", "HOEK", "H10"))
sip.logout()
```

#### Use timeseries
``` python
from lmwsip import LmwSip
from datetime import datetime, timedelta
from pprint import pprint

end   = datetime.now()
start = end - timedelta(hours=1)

sip = LmwSip("USER", "PASS")
pprint(sip.timeSerie("WN", "HOEK", "H10", start, end).ts)
```

### lmwsip.run
```
$ python -m lmwsip.run /tmp/hoek-h10.sip 
> [LI USER,PASS]
< [! ]
> [TI LMW]
< [! 08-SEP-20 12:03:27]
> [WN LMW,HOEK,H10,-01:00,08-09-2020,11:50,DATA]
< [! -17/50;-21/50;-24/50;-26/50;-27/50;-28/50;-28/50]
> [LO]
< [! ]
```

## Unit tests

The code containts a python unittest.

This code runs a dummy sip server and runs a number of test against the dummy
server.

## Git pre commit hook

There is a pre-commit `githooks/pre-commit' with two functions:
 * Updating the `__version__` in the module from setup.py
 * Running the unit test code.
 * Running a syntaxt test.
