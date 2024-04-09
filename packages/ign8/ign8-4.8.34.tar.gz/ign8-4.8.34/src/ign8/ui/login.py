import os
import sys
import pprint
from ..common import prettyllog
import subprocess
import hvac
import requests
import psutil
import time


def is_firefox_running():
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == 'firefox-esr' or process.info['name'] == 'firefox' or process.info['name'] == 'firefox-bin' or process.info['name'] == 'firefox-esr-bin':
            return True
    return False



def writekv(path, keypair):
  ign8_vault_url  = os.environ.get("VAULT_URL", "https://vault.openknowit.com")
  ign8_vault_token = os.environ.get("VAULT_TOKEN", "s.5Y9pZ4x6y3sZ4y3s")
  client = hvac.Client(
    url=ign8_vault_url,
    token=ign8_vault_token,
  )
  create_response = client.secrets.kv.v2.create_or_update_secret(
    path=path,
    secret=dict(keypair),
  )
  prettyllog("ui", "login", "writekv", "wrote keypair to vault", 000 , "Start", severity="INFO")
  return 0

def firefox_cookies():
  mymachineid = read_machine_id()

  prettyllog("ui", "login", "firefox_cookies", "extracting firefox cookies", 000 , "Start", severity="INFO")
  # change to my home directory
  mydir = os.path.expanduser("~")+ "/.mozilla/firefox"
  os.chdir(mydir)
  prettyllog("ui", "login", "firefox_cookies", "changed to firefox directory", 000 , "Start", severity="INFO")
  filename = find_file(mydir, "cookies.sqlite")
  # copy the file to my home directory/tmp for processing
  myhome = os.path.expanduser("~")
  mydir = myhome + "/tmp"
  os.system("mkdir -p " + mydir + '>/dev/null 2>&1' )
  mycommand = "cp " + filename + " " + mydir + "/cookies.tmp.sqlite"
  os.system(mycommand)
  prettyllog("ui", "login", "firefox_cookies", "copied cookies.sqlite to tmp", 000 , "Start", severity="INFO")
  # connect to the database
  mysql = "SELECT value FROM moz_cookies where host like 'ignite.openknowit.com'"
  command =  ["sqlite3", "/home/jho/tmp/cookies.tmp.sqlite", mysql]
  mycookiedata = subprocess.run(command, capture_output=True)
  mysplit = mycookiedata.stdout.splitlines()
  for line in mysplit:
    line = line.decode('utf-8')
    mysplit = line.split("|")
    count = 0
    for item in mysplit:
      mykeypair = {
        "machineid": mymachineid,
        "cookie": item
      }
      writekv(item, mykeypair)
      count = count + 1
  prettyllog("ui", "login", "firefox_cookies", "extracted cookies", count , "Start", severity="INFO")
  return 0







def find_file(directory, filename):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None


def extractcookie():
  # change to my home directory
  # is firefox running?
  if is_firefox_running():
    firefox_cookies()

  else:
    print("firefox is not running")
    return 0
  
def gethostifo():
  hostdata = subprocess.run(["hostnamectl"], capture_output=True)
  if hostdata.returncode != 0:
    prettyllog("ui", "login", "gethostinfo", "failed to read host info", 000 , "Start", severity="ERROR")
    return 1
  hoststdout = hostdata.stdout
  hoststdout = hoststdout.decode('utf-8')
  mysplit = hoststdout.splitlines()
  myhostjson = {}
  for line in mysplit:
    mykey = line.split(": ")[0].strip()
    myvalue = line.split(": ")[1].strip()
    myhostjson[mykey] = myvalue
  return myhostjson

  
def read_netbox_data():
  netboxcrds =  {}
  try:
    mynetboxtoken = os.getenv('IGN8_NETBOX_TOKEN')
    netboxcrds['token'] = mynetboxtoken
  except:
    prettyllog("ui", "login", "read_netbox_data", "failed to read netbox token", 000 , "Start", severity="ERROR")

  try:
    mynetboxurl = os.getenv('IGN8_NETBOX_URL')
    netboxcrds['url'] = mynetboxurl

  except:
    prettyllog("ui", "login", "read_netbox_data", "failed to read netbox url", 000 , "Start", severity="ERROR")

  if len(netboxcrds) != 2:
    prettyllog("ui", "login", "read_netbox_data", "failed to read netbox credentials", 000 , "Start", severity="ERROR")
    # try to read from the vault
    try:
      myvaulturl = os.environ('VAULT_URL')
      myvaulttoken = os.environ('VAULT_TOKEN')
      client = hvac.Client(
        url=myvaulturl,
        token=myvaulttoken,
      )
      netboxcrds = client.secrets.kv.v2.read_secret_version(path='ign8/netbox')
      mynetboxurl = netboxcrds['data']['url']
      mynetboxtoken = netboxcrds['data']['token']
    except:
      prettyllog("ui", "login", "read_netbox_data", "failed to read netbox credentials from vault", 000 , "Start", severity="ERROR")
      return 1
    

  try: 
    myhostname = os.getenv('HOSTNAME')
  except:
    prettyllog("ui", "login", "read_netbox_data", "failed to read hostname", 000 , "Start", severity="ERROR")
    return 1
    

  myurl = mynetboxurl + "/api/dcim/devices/?name=" + myhostname
  myheaders = {
    "Authorization": "Token " + mynetboxtoken
  }
  response = requests.get(myurl, headers=myheaders)
  if response.status_code != 200:
    prettyllog("ui", "login", "read_netbox_data", "failed to read netbox data", 000 , "Start", severity="ERROR")
    return 1  
  mydata = response.json()
  if mydata['count'] == 0:
    # no data found
    prettyllog("ui", "login", "read_netbox_data", "failed to read netbox data", 000 , "Start", severity="INFO")




   
   
  
def read_machine_id():
  with open('/etc/machine-id', 'r') as file:
    data = file.read().replace('\n', '')
  return data


def updatecmdb():
  mymachineid = read_machine_id()
  read_netbox_data()
  mykeypair = {
    "machineid": mymachineid,
    "username": "admin",
    "password": "admin123"
  }



def main():
  while True:
    hostinfo = gethostifo()
    print(hostinfo)


    prettyllog("ui", "login", "init", "initializing login", 000 , "Start", severity="INFO")
    updatecmdb()
    keypair = {"username": "admin", "password": "admin123"}  
    writekv("igniteui", keypair)
    extractcookie()
    time.sleep(5)
  return 0

