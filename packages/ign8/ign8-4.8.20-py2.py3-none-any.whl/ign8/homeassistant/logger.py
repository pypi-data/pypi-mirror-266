from requests import get
import redis
import json
import os
import time
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pprint

homeassistanturl = os.getenv("IGN8_HOMEASSISTANT_URL")
homeassistanttoken = os.getenv("IGN8_HOMEASSISTANT_TOKEN")

ESURL = os.getenv('IGN8_ELASTICSEARCH_URL')
try: 
    ESPORT = os.getenv('IGN8_ELASTICSEARCH_PORT')
except:
    ESPORT = 443
try: 
    ESINDEX = os.getenv('IGN8_HOMEASSISTENT_INDEX')
except:
    ESINDEX = "homeassistant"

ESUSER = os.getenv('IGN8_ELASTICSEARCH_USERNAME')
ESPASS = os.getenv('IGN8_ELASTICSEARCH_PASSWORD')




r = redis.StrictRedis(host='localhost', port=6379, db=0)

es= Elasticsearch(ESURL, basic_auth=(ESUSER, ESPASS))

def create_index(index):
  es = connect()
  try:
    resp = es.indices.create(index=index)
    return resp
  except:
    return True
   

def connect():
  url = os.getenv('ELASTICSEARCH_URL')
  username = os.getenv('ELASTICSEARCH_USERNAME')
  password = os.getenv('ELASTICSEARCH_PASSWORD')
  es = Elasticsearch(url, basic_auth=(username, password))
  if es.info():
    return es
  else:
    return None


def create_index(es,index):
    try: 
      resp = es.indices.create(index=index)
      return resp
    except:
      return True





headers = {
    "Authorization": "Bearer " + homeassistanttoken,
    "content-type": "application/json",
}

def create_doc(es,index, doc):
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
    create_index(es, ESINDEX)
    response = get(homeassistanturl, headers=headers, verify=False)
    return True

def get_events():
    try:
        url = homeassistanturl + "events"
        response = get(url, headers=headers, verify=False)
        return response.json()
    except Exception as e:
        return False

def turn_on():
  #url: http://localhost:8123/api/states/light.study_light
  #method: POST
  #headers:
  #  authorization: 'Bearer TOKEN'
  #  content-type: 'application/json'
  #payload: '{"state":"on"}'
  url = homeassistanturl + "states"


    

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
    print(check_connection())
    es = connect()
    if es.info():
        print("Connected to ES")
    else:
        print("Failed to connect to ES")
        return False
    pprint.pprint(create_index(es, ESINDEX))


    
    while True:
      logbook = get_logbook()
      for log in logbook:
          log['@timestamp'] = log['when']
          rediskey = log['when'] 
          if r.exists(rediskey):
            pass
          else:
            r.set(rediskey, 1)
            create_doc(es,ESINDEX, log)
            print("New log")
            pprint.pprint(log)
      time.sleep(1)



if __name__ == "__main__":
    main()

