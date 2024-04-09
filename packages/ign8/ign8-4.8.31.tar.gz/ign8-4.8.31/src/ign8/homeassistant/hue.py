import requests
from requests import get
import sys

import hvac
import os
import pprint
from datetime import datetime

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

client = hvac.Client(url=os.getenv('VAULT_ADDR'), token=os.getenv('VAULT_TOKEN'))

def age(datestring):
    # Convert the input date string to a datetime object
    birth_date = datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S")
    
    # Get the current datetime
    current_datetime = datetime.now()

    # Calculate the age in seconds
    age_in_seconds = (current_datetime - birth_date).total_seconds()

    return int(age_in_seconds)

def save_hue_token():
    client.secrets.kv.v2.create_or_update_secret(
        path='hue',
        secret=dict(token=os.getenv('HUE_TOKEN'))
    )



def get_hue_token():
    return client.secrets.kv.v2.read_secret_version(path='hue')['data']['data']['token']

def get_hue_light(token, service):
    url = f"https://{os.getenv('HUE_BRIDGE_IP')}/api/{token}/{service}"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def turn_on(host):
    url = "http://" + host + "/rpc/Switch.Set?id=0&on=true"
    response = get(url)
    return response.json()

def turn_off(host):
    url = "http://" + host + "/rpc/Switch.Set?id=0&on=false"
    response = get(url)
    return response.json()






def main():
    token = os.getenv('HUE_TOKEN')
    #rules = get_hue_light(token, "rules")
    sensors = get_hue_light(token, "sensors")
    mysensors = {}
    for sensor in sensors:
        try: 
            name = sensors[sensor]['name']
            try:
                state = sensors[sensor]['state']['buttonevent']
                triggered = sensors[sensor]['state']['lastupdated']

                pressage = age(triggered)
                print("%-30s %-20s %-20s %-20s" % (name, state, triggered, pressage))
                if pressage > 3640:
                    state = None
                name2 = name + "_2"

                if state == 20:
                    turn_on(name)
                if state == 21:
                    turn_off(name)

                if state == 23:
                    print(name2 + " " + str(state))
                    turn_on(name2)
                if state == 22:
                    print(name2 + " " + str(state))
                    turn_off(name2)
            except:
                state = None


            mysensors[name] = state
        except:
            continue
    


if __name__ == '__main__':
    while True:
        main()
        print("----------------------------")
        
        


