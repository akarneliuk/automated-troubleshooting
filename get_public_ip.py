#!/usr/bin/env python
#(c)2019-2021, karneliuk.com

"""
This tool provides the resultion of the public IP address to the author.
"""

# Modules
import datetime
import requests
import yaml

# Local modules
import helpers.shared as hs

# Body
if __name__ == "__main__":
    # Import configuration file
    config = hs.import_config("./config.yml")

    # Polling the public IP
    t1 = datetime.datetime.now()
    ip = requests.get(url=config["urls"]["geo_ip"]).json()
    print(f"Request started at: {t1}\nRequested completed within: {datetime.datetime.now() - t1}\nYour IP is: {ip['ip']}")