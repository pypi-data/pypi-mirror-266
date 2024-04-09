import requests
import hvac
import os
import pprint
client = hvac.Client(url=os.getenv('VAULT_ADDR'), token=os.getenv('VAULT_TOKEN'))

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






def main():
    #save_hue_token()
    token = get_hue_token()
    lights = get_hue_light(token, "lights")
    sensors = get_hue_light(token, "sensors")
    rules = get_hue_light(token, "rules")
    groups = get_hue_light(token, "groups")
    config = get_hue_light(token, "config")

    for rule in rules:
        print("--------------------------------------------------- ")
        for item in rules[rule]:
            print(item, rules[rule][item])
        print("--------------------------------------------------- ")



    for light in lights:
        print("--------------------------------------------------- ")
        for item in lights[light]:
            print(item, lights[light][item])
                  
        
        print("--------------------------------------------------- ")

    for sensor in sensors:
        print(sensors[sensor]['name'])
        #for item in sensors[sensor]:

#           print("--------------------------------------------------- ")
#           print(item, sensors[sensor][item])
#           print("--------------------------------------------------- ")



if __name__ == '__main__':
    main()


