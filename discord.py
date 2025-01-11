import requests
import json

def retrieveImage():
    headers = {
         
    }
    r = requests.get('https://discord.com/api/v9/channels/1327749868608815276/messages?limit=1', headers=headers)
    # print(r.body)
    thing = json.loads(r.text)
    return thing