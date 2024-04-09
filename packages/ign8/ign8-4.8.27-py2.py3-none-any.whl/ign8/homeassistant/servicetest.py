from requests import get
import os
import pprint

homeassistanturl = os.getenv("IGN8_HOMEASSISTANT_URL")
homeassistanttoken = os.getenv("IGN8_HOMEASSISTANT_TOKEN")

headers = {
    "Authorization": "Bearer " + homeassistanttoken,
    "content-type": "application/json",
}

def turnoff(entity_id):
    
        url = homeassistanturl + "services/switch/turn_off"
        data = {
            "entity_id": entity_id
        }
        response = get(url, headers=headers, json=data, verify=False)
        pprint.pprint(response.status_code)
        pprint.pprint(response.reason)
        return response.json()
        return False
    
def turnon(entity_id):
        url = homeassistanturl + "services/switch/turn_on"
        data = {
            "entity_id": entity_id
        }
        response = get(url, headers=headers, json=data, verify=False)
        pprint.pprint(response.status_code)
        return response.json()
        return False
    

def get_services():
    try:
        url = homeassistanturl + "services"
        response = get(url, headers=headers, verify=False)
        pprint.pprint(response.status_code)
        return response.json()
    except Exception as e:
        return False
    
def main():
    turnoff("switch.hall_switch_0")
    turnon("switch.hall_switch_0")



if __name__ == "__main__":
    main()

