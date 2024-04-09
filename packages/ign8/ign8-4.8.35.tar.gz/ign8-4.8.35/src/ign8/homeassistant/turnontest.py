import os
import json
import pprint


api_url = "http://hal9000l.jakobholst.dk:8123/api"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MjQ0NzNhOWVmZWU0ZTNmYWNmMDM4MjY1MzdhYWJhMiIsImlhdCI6MTcwOTE1MzUwOCwiZXhwIjoyMDI0NTEzNTA4fQ.lqW4XoCRc6-q-pBv7bJ3aVhSdFN3HTVCdZWx0zSna_M"
client = Client( api_url, token)

service = client.get_domain("switch")  # Gets the light service domain from Home Assistant
service.turn_on(entity_id="hall_switch_0")  # Turns on the light with the entity_id "light.study_light"

entities = client.get_entities()


keys = entities.keys()
key ="switch"
for item in entities[key]:
    if item[0] == "entities":
        for entity in item[1]:
            print(entity)



            
            
    print("--------------------------")















