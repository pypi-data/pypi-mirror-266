import os
import pprint
from homeassistant_api import Client
from homeassistant_api import State


api_url = "http://hal9000l.jakobholst.dk:8123/api"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MjQ0NzNhOWVmZWU0ZTNmYWNmMDM4MjY1MzdhYWJhMiIsImlhdCI6MTcwOTE1MzUwOCwiZXhwIjoyMDI0NTEzNTA4fQ.lqW4XoCRc6-q-pBv7bJ3aVhSdFN3HTVCdZWx0zSna_M"


client = Client( api_url, token)

entities = client.get_entities()
pprint.pprint(entities)










