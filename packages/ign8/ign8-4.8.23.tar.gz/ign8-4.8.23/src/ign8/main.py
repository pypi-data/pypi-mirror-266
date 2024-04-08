from .common import prettylog
import os
import subprocess
import sys

def getenv(key, default):
    if key in os.environ:
        return os.environ[key]
    else:
        return default

def main():
    prettylog("INFO", )
    return True

def in_venv():
    return sys.prefix != sys.base_prefix

def init_service():
    prettylog("INFO", "Init service")

def start_service():
    prettylog("INFO", "start service")

def stop_service():
    prettylog("INFO", "stop service")

def serve():
    while True:
        prettylog("info" , "Start loop")
    return True
