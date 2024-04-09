from .common import prettylog
import os
import subprocess
import time
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

    servicefile = "\
[Unit]\
Description=Ign8 Service\
After=network.target\
\
[Service]\
Type=simple\
User=ign8\
ExecStart=/usr/local/bin/ign8 serve\
Restart=always\
\
[Install]\
WantedBy=multi-user.target\
"
    servicefilename = "/etc/systemd/system/ign8.service"
    write_string_to_file(servicefilename, servicefile )
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "ign8"])
    
    



def write_string_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)
    
    # Create and overwrite the service file"






def start_service():
    prettylog("INFO", "start service")
    subprocess.run(["systemctl", "start", "ign8"])


def stop_service():
    prettylog("INFO", "stop service")
    subprocess.run(["systemctl", "stop", "ign8"])

def serve():
    while True:
        prettylog("info" , "Start loop")
        time.sleep(1)