#!/usr/bin/env python3

import sys
import getopt
import argparse
import logging
from lmwsip import LmwSip

def run(args):
    logging.basicConfig(level=args.debug)
    logging.debug("lmwsip.run %s" % args)
    try:
        lmwsip = LmwSip(host=args.host, port=args.port,
                        ssl=not args.unencrypted,
                        check_ssl=not args.acceptssl,
                        cleartelnet=args.cleartelnet)
    except Exception as e:
        print("Connect to lmw failed: %s" % e)
        exit(1)
    for f in args.files:
        for cmd in f:
            cmd = cmd.replace('{DATE}', args.date)
            cmd = cmd.replace('{TIME}', args.time)
            cmd = cmd.replace('\n', '\r')
            print("> [%s]" % (cmd.strip('\r')))
            try:
                lmwsip.send(cmd)
                print("< [%s]" % (lmwsip.recv().strip('\r')))
            except:
                pass
    try:
        lmwsip.closesocket()
    except:
        pass

def main():
    lastTime=LmwSip(host=None).lasttime("H10")
    parser = argparse.ArgumentParser(description="Run a sip file.")
    parser.add_argument("-u", "--unencrypted", action="store_true",
                        help="Run a sip connection without ssl")
    parser.add_argument("-a", "--acceptssl", action="store_true",
                        help="Accept ssl certificate")
    parser.add_argument("-c", "--cleartelnet", action="store_true",
                        help="Clear telnet protocol in tcp session")
    parser.add_argument("-H", "--host", action='store',
                        default="sip-lmw.rws.nl",
                        help="Host to connect to")
    parser.add_argument("-p", "--port", action='store', type=int, default=443,
                        help="Port to connect to")
    parser.add_argument("-d", "--date", action='store',
                        default=lastTime["day"],
                        help="Date replacement string [DD-MM-YYYY]")
    parser.add_argument("-t", "--time", action='store',
                        default=lastTime["time_of_day"],
                        help="Time replacement string [HH:MM]")
    parser.add_argument("-D", "--debug", action='store',
                        default="WARN",
                        help="Debug level")
    parser.add_argument("files", type=argparse.FileType('r'), nargs="+",
                        help="Sip files to run")
    run(parser.parse_args())

if __name__ == "__main__":
    main()
