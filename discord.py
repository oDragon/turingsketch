import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def retrieveImage():
    headers = {
        'authorization': os.getenv('DISCORD_AUTH_TOKEN')
    }
    r = requests.get('https://discord.com/api/v9/channels/1327749868608815276/messages?limit=1', headers=headers)
    thing = json.loads(r.text)
    
    return thing