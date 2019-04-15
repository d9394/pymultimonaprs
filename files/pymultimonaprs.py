#!/usr/bin/python2

import json
import threading
from time import sleep
import sys
import logging
import logging.handlers
import argparse
import signal

from multimon import Multimon
import beacon
from gate import IGate
from frame import APRSFrame, InvalidFrame

parser = argparse.ArgumentParser(description='HF2APRS-IG Gateway.')
parser.add_argument('-c', dest='config', default='/etc/pymultimonaprs/pymultimonaprs.json', help='Use this config file')
parser.add_argument('--syslog', action='store_true', help='Log to syslog')
parser.add_argument('--logfile', dest='logfile', help='Log to file')
parser.add_argument('-v', '--verbose', action='store_true', help='Log all traffic - including beacon')
args = parser.parse_args()

config = json.load(open(args.config))

logger = logging.getLogger('pymultimonaprs')
loglevel = logging.DEBUG if args.verbose else logging.INFO
logger.setLevel(loglevel)
if args.syslog:
	loghandler = logging.handlers.SysLogHandler(address = '/var/log')
	formater = logging.Formatter('pymultimonaprs: %(message)s')
	loghandler.setFormatter(formater)
elif args.logfile:
	loghandler = logging.FileHandler(args.logfile)
	formatter = logging.Formatter('[%(asctime)s] %(levelname)+8s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	loghandler.setFormatter(formatter)
else:
	loghandler = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter('[%(asctime)s] %(levelname)+8s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	loghandler.setFormatter(formatter)
logger.addHandler(loghandler)

def mmcb(tnc2_frame):
	try:
		frame = APRSFrame()
		frame.import_tnc2(tnc2_frame)
		if config['append_callsign']:
			frame.path.extend([u'qAR', config['callsign']])

		# Filter packets from TCP2RF gateways
		reject_paths = set(["TCPIP", "TCPIP*", "NOGATE", "RFONLY"])
		# '}' is the Third-Party Data Type Identifier (used to encapsulate pkgs)
		# indicating traffic from the internet
		if len(reject_paths.intersection(frame.path)) > 0 or frame.payload.startswith("}"):
			logger.debug("rejected: %s" % frame.export(False))
		else:
			ig.send(frame)

	except InvalidFrame:
		pass

def bc():
	bcargs = {
		'lat': float(config['beacon']['lat']),
		'lng': float(config['beacon']['lng']),
		'callsign': config['callsign'],
		'table': config['beacon']['table'],
		'symbol': config['beacon']['symbol'],
		'comment': config['beacon']['comment'],
		'ambiguity': int(config['beacon'].get('ambiguity', 0)),
		'beacon': config['beacon']['beacon'],
	}
	bcargs_status = {
		'callsign': config['callsign'],
		'status': config['beacon']['status'],
	}
	bcargs_weather = {
		'callsign': config['callsign'],
		'weather': config['beacon']['weather'],
	}
	while True:
		# Position
		frame = beacon.get_beacon_frame(**bcargs)
		if frame:
			ig.send(frame)

		# Status
		frame = beacon.get_status_frame(**bcargs_status)
		if frame:
			ig.send(frame)

		# Weather
		frame = beacon.get_weather_frame(**bcargs_weather)
		if frame:
			ig.send(frame)

		sleep(int(config['beacon']['send_every']))

logger.info("Starting pymultimonaprs")

preferred_protocol = config.get("preferred_protocol", "any").lower()

ig = IGate(config['callsign'], config['passcode'], config['gateway'], preferred_protocol)
mm = Multimon(mmcb,config)

def signal_handler(signal, frame):
	logger.info("Stopping pymultimonaprs")
	ig.exit()
	mm.exit()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start beacon in main thread
bc()
