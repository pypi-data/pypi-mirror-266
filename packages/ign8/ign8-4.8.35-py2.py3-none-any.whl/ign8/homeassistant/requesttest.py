from requests import post

url = "http://hal9000:8123/api/services/switch/turn_on"
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI1MjQ0NzNhOWVmZWU0ZTNmYWNmMDM4MjY1MzdhYWJhMiIsImlhdCI6MTcwOTE1MzUwOCwiZXhwIjoyMDI0NTEzNTA4fQ.lqW4XoCRc6-q-pBv7bJ3aVhSdFN3HTVCdZWx0zSna_M"}
data = {"entity_id": "switch.hall_switch_0"}
response = post(url, headers=headers, json=data)
print(response.text)