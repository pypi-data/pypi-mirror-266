from .common import prettylog
import os
import subprocess
import time
import sys
import redis
import json

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

    servicefile = "\
[Unit]\n\
Description=Ign8 Service\n\
After=network.target\n\
\n\
[Service]\n\
Type=simple\n\
User=ign8\n\
ExecStart=/usr/local/bin/ign8 serve\n\
Restart=always\n\
\n\
[Install]\n\
WantedBy=multi-user.target\n\
"
    servicefilename = "/etc/systemd/system/ign8.service"
    write_string_to_file(servicefilename, servicefile )
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "ign8"])

def check_redis():
    prettylog("INFO", "Check redis")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.ConnectionError:
        prettylog("ERROR", "Redis is not running")
        prettylog("INFO", "Starting Redis")
        subprocess.run(["systemctl", "start", "redis"])
    else:
        prettylog("INFO", "Redis is running")

    
    



def write_string_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)
    
    # Create and overwrite the service file"

def read_config():
    open('/etc/ign8/config.json', 'r').read()
    myconfig = json.loads(open('/etc/ign8/config.json', 'r').read())
    prettylog("INFO", "Read config", myconfig)
    return myconfig








def start_service():
    prettylog("INFO", "start service")
    subprocess.run(["systemctl", "start", "ign8"])


def stop_service():
    prettylog("INFO", "stop service")
    subprocess.run(["systemctl", "stop", "ign8"])

def serve():
    init_service()
    while True:
        prettylog("info" , "Start loop")
        time.sleep(1)
        check_redis()
        myconfig = read_config()
