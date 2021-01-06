#!/usr/bin/env python
#(c)2019-2021, karneliuk.com

"""
This tool provides the resultion of the public IP address to the author.
"""

# Modules
import datetime
import requests

# Variables
url = "https://api.myip.com"

# Body
if __name__ == "__main__":
    t1 = datetime.datetime.now()
    ip = requests.get(url=url).json()
    print(f"Request started at: {t1}\nRequested completed within: {datetime.datetime.now() - t1}\nYour IP is: {ip['ip']}")