#!/usr/bin/env python
import sys
from rq import Connection, Worker
from redis import Redis

# Preload libraries
import json
import copy
from bisect import bisect_left
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from globalsettings import blockSettings
import logging.config
import convergenceProcessor
import logging.config
import requests
import consensusEmulator
import redisUtilities
import blockUtilities
import encryptionUtilities

# put in BSD and other license clauses?

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection(Redis('redis', 6379)):
    qs = ['default']

    w = Worker(qs)
    w.work()
