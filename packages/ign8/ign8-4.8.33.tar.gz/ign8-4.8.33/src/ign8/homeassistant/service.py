from requests import get
import json
import os
import time
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pprint
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)


homeassistanturl = os.getenv("IGN8_HOMEASSISTANT_URL")
homeassistanttoken = os.getenv("IGN8_HOMEASSISTANT_TOKEN")

def connect():
  url = os.getenv('ELASTICSEARCH_URL')
  username = os.getenv('ELASTICSEARCH_USERNAME')
  password = os.getenv('ELASTICSEARCH_PASSWORD')
  es = Elasticsearch(url, basic_auth=(username, password))
  if es.info():
    return es
  else:
    return None


def create_index(index):
  es = connect()
  try:
    resp = es.indices.create(index=index)
    return resp
  except:
    return True





headers = {
    "Authorization": "Bearer " + homeassistanttoken,
    "content-type": "application/json",
}

def create_doc(index, doc):
  es = connect()
  try:
    resp = es.index(index=index, body=doc)
    return resp
  except:
    return None
def print_epoch_pretty(epoch_timestamp):
    # Convert epoch timestamp to datetime object
    dt_object = datetime.utcfromtimestamp(epoch_timestamp)

    # Print the datetime object in a pretty format
    print(dt_object.strftime("%Y-%m-%d %H:%M:%S"))


def check_connection():
    create_index("ign8")
    response = get(homeassistanturl, headers=headers, verify=False)
    data = response.json()
    data['@timestamp'] = print_epoch_pretty(int(time.time()))
    create_doc("ign8", data)
    return True

def get_events():
    try:
        url = homeassistanturl + "events"
        response = get(url, headers=headers, verify=False)
        return response.json()
    except Exception as e:
        return False

def turn_on(host):
  #curl "http://${ip}/rpc/Switch.Set?id=0&on=false"
  url = "http://" + host + "/rpc/Switch.Set?id=0&on=true"
  response = get(url, headers=headers, verify=False)
  return response.json()

def turn_off(host):
    #curl "http://${ip}/rpc/Switch.Set?id=0&on=false"
    url = "http://" + host + "/rpc/Switch.Set?id=0&on=false"
    response = get(url, headers=headers, verify=False)
    return response.json()


    

def get_states():
    try:
        url = homeassistanturl + "states"
        response = get(url, headers=headers, verify=False)
        return response.json()
    except Exception as e:
        return False
def get_logbook():
    try:
        url = homeassistanturl + "logbook"
        response = get(url, headers=headers, verify=False)
        return response.json()
    except Exception as e:
        return False
def get_state(entity_id):
    try:
        url = homeassistanturl + "states/" + entity_id
        response = get(url, headers=headers, verify=False)
        return response.json()
    except Exception as e:
        return False
    
    
def change_state(entity_id, state):
    try:
        url = homeassistanturl + "states/" + entity_id
        data = {"entity_id": entity_id}
        response = get(url, headers=headers, data=json.dumps(data), verify=False)
        return response.json()
    except Exception as e:
        return False

def main():
    myparring = [
                    { "press": "Stueswitch", "switch": "stue" },
                    { "press": "køkkenswitch", "switch": "koekken" },

                ]
    while True:

        logbook = get_logbook()
        if type(logbook != "bool"):
          for log in logbook:
            if log['name'] == "Stueswitch":
                if "second button pressed initially" in log['message']:
                    mykey = log['when'] + log['message']
                    if r.exists(mykey): 
                        continue
                    else:
                        turn_off("stue")
                        r.set(mykey, "true")
                        pprint.pprint(log)
                if "first button pressed initially" in log['message']:
                    mykey = log['when'] + log['message']
                    if r.exists(mykey): 
                        continue
                    else:
                        turn_on("stue")
                        r.set(mykey, "true")
                        pprint.pprint(log)


            if log['name'] == "Hall switch":
                try:
                  if "fourth button pressed initially" in log['message']:
                    mykey = log['when'] + log['message']
                    if r.exists(mykey): 
                        continue
                    else:
                        turn_off("koekken")
                        turn_off("koekken")
                        turn_off("sovevaerelse")
                        turn_off("stue")
                        turn_off("hall")
                        turn_off("bad1st")
                        turn_off("badstuen")
                        turn_off("bryggers")
                        r.set(mykey, "true")
                        pprint.pprint(log)

                  if "third button pressed initially" in log['message']:
                    mykey = log['when'] + log['message']
                    if r.exists(mykey): 
                        continue
                    else:
                        turn_on("koekken")
                        turn_on("sovevaerelse")
                        turn_on("stue")
                        turn_on("hall")
                        turn_on("bad1st")
                        turn_on("badstuen")
                        turn_on("bryggers")
                        r.set(mykey, "true")
                        pprint.pprint(log)
                except: 
                  pass





if __name__ == "__main__":
    main()

