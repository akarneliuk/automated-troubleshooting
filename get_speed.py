#!/usr/bin/env python
#(c)2019-2021, karneliuk.com

"""
This tool mails the results of the speedtest to the destination mail address.
There is an assumption that the official Ookla SpeedTest CLI is installed on your system and is available for the user.

Replace the following variables accordingly:
  - mail['server']      : your SMTP mail server
  - mail['password']    : your password for mail account
  - mail['source']      : your mail account, which will be used by the script to send the e-mail
  - mail['destination'] : mail account, which is used to receive the mail from the script
"""

# Modules
import datetime
import subprocess
import json
import ssl
from getpass import getpass

# Variables
mail = {'server': 'mail.com', 'port': 465, 'password': getpass('Mail password > '), 'source': 'test@mail.com', 'destination': 'test@mail.com'}

# Body
if __name__ == "__main__":
    t1 = datetime.datetime.now()
    speed_details = json.loads(subprocess.run(['speedtest', '-f', 'json'], stdout=subprocess.PIPE).stdout.decode('utf-8'))
    result = f"Request started at: {t1}\nRequested completed within: {datetime.datetime.now() - t1}\nYour Downlink BW is {speed_details['download']['bandwidth'] * 8} bps and Uplink BW is {speed_details['upload']['bandwidth'] * 8} bps"
    print(result)

    # Mailing report
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(mail['server'], port=mail['port'], context=context) as server:
        server.login(mail['source'], mail['password'])
        server.sendmail(from_addr=mail['source'], to_addrs=mail['destination'], msg=result)