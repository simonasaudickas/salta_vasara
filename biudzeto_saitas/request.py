import requests
import json

r= requests.get('http://192.168.0.112:8000/api')
j = json.loads(r.text)
for i in j:
    print(i)