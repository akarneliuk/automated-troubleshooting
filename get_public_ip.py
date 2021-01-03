#!/usr/bin/env python
#(c)2021, karneliuk.com

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
    ip = requests.get(url=url).json()
    print(f"Request completed at: {datetime.datetime.now()}\nYour IP is: {ip['ip']}")