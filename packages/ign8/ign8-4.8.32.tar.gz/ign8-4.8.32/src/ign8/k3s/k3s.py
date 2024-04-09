import requests
import os
import urllib3
from ..common import prettyllog
from kubernetes import client, config


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def status():
  print()

def check_k3s():
  try:
    response = requests.get('https://localhost:6443', verify=False)
    if response.status_code == 200:
      return True
    else:
      return False
  except:
    return False
  
def start_k3s():
  if check_k3s():
    print("K3s is already running")
  else:
    os.system("sudo systemctl start k3s")
    os.system("sudo systemctl enable k3s")
    print("K3s started and enabled")

def stop_k3s():
  if check_k3s():
    os.system("sudo systemctl stop k3s")
    os.system("sudo systemctl disable k3s")
    print("K3s stopped and disabled")
  else:
    print("K3s is not running")


def service():
  prettyllog("Starting k3s service", "info", "k3s", "service", "k3s", "INFO")
  config.load_kube_config()
  v1 = client.CoreV1Api()
  print("Listing pods with their IPs:")
  ret = v1.list_pod_for_all_namespaces(watch=False)
  for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))



  