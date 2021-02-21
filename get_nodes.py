#!/usr/bin/env python
#(c)2019-2021, karneliuk.com

"""
This tool allows you to get the information about the hosts alive within the provided range.
Two options available:
  - local search. In this case the host searches for all the neighbors within all its subnets.
    Once found, it tries to figure out what is the manufacturer of the connected node. The
    result is returned in the YAML format.
  - remote search. In this case the host searches for all the hosts alive within the specific
    subnet and returns a list of them in YAML format (in development)
"""


# Modules
import requests
import os
import subprocess
import platform
import sys
import re
import json
import socket
import argparse
import datetime


# Local modules
import helpers.shared as hs


# User-defined functions
def args_parser():
    """
    This function contains information about arguments you provide for the script to run
    """
    parser = argparse.ArgumentParser(description="Collect the live hosts in your network. Local or remote checks are possibl.")

    parser.add_argument("--mode", dest="mode", default="local",
                        help="Provide the execution mode. Options: local or remote.")
    parser.add_argument("--targets", dest="targets", type=str, default="",
                        help="Provide the list of the IP ranges to be checked. Works with remote.")
    parser.add_argument("--detailed", dest="detailed", type=bool, default=False,
                        help="Specify if you want to get detailed info about local neigbors. Works with local.")

    result = parser.parse_args()
    result.targets = result.targets.split(",")

    if result.mode not in {"local", "remote"}:
        sys.exit("Wrong operations mode. Must be local or remote")

    if result.mode == "remote" and not result.targets:
        sys.exit("The remote mode is chosen, but no ranges provided.")

    return result


def get_host_details():
    """
    This function collects the host details
    """
    # Collecting the platform details
    hp = platform.uname()

    # Collecting hostname
    hostname = socket.gethostname()

    # Collecting IP addresses of the host
    ip_address = socket.gethostbyname_ex(hostname)

    result = {"hp": hp, "hostname": hostname, "ipv4_addresses": ip_address[-1]}

    return result


def awake_neighbors(ip_list: list, mode: str):
    """
    This functions runs fping for the connected subnets to force hosts to appear
    in ARP table
    """
    # Local vars
    result = []
    # Adding the prefix (default assumption that prefix is /24)
    if mode == "local":
        ip_list = [f"{'.'.join(ip.split('.')[0:3])}.0/24" for ip in ip_list]

    for entry in ip_list:
        raw_data = subprocess.run(["fping", "-g", entry, "-a", "-q"], capture_output=True).stdout.decode("utf-8")
        result.extend(raw_data.splitlines())
    
    return result


def get_file(url: str, rdir: str):
    """
    This function downloads the file from the provided URL and stores that locally
    """
    # Getting filename
    filename = url.split("/")[-1]

    # Obtainining the file content
    if os.path.exists(f"{rdir}/{filename}"):
        print(f"The file '{rdir}/{filename}' already exists. Using local copy...")

        with open(f"{rdir}/{filename}", "rb") as f:
            result = f.read()

    else:
        print(f"The file '{rdir}/{filename}' does not exist. Downloading...")
        # Creating the directory to save files
        if not os.path.exists(rdir):
            os.mkdir(rdir)

        # Downloading file
        response = requests.get(url=url)
        result = response.content

        # Saving the file
        with open(f"{rdir}/{filename}", "wb") as f:
            f.write(result)

    result = result.decode("utf-8")

    return result


def get_neighbors(hp):
    """
    This function collects the ARP table from your local host
    """
    # Local vars
    result = []
    nix_systems = {"Darwin", "Linux"}

    # Collecting ARP table
    if hp.system in nix_systems:
        try:
            raw_output_ipv4 = subprocess.run(["arp", "-an"], capture_output=True).stdout.decode("utf-8")
        except:
            sys.exit("Something went wrong during colletion of the ARP table")

    # Convering the raw output to the list of lists
    if raw_output_ipv4:
        raw_lol = [r.split(" ") for r in raw_output_ipv4.splitlines()]

        # Creating dictionary out of raw ARP table
        for entry in raw_lol:
            if not re.match(".*incomplete.*", entry[3]):
                tc = {}

                # Selecting IP
                tc.update({"ip": re.sub("\(([\d\.]+)\)", "\g<1>", entry[1])})
                tc.update({"family": 4})

                # Selecting MAC
                temp_mac = re.sub("\(([a-zA-Z0-9:]+)\)", "\g<1>", entry[3])
                # Modifying MAC to canonical if not
                temp_mac = "-".join([f"0{elem}" if len(elem) == 1 else elem for elem in temp_mac.split(":")])
                tc.update({"mac": temp_mac.upper()})

                if hp.system == "Darwin":
                    # Selecting interface
                    tc.update({"interface": entry[5]})

                    # Selecting type
                    if tc["mac"].split("-")[0] == "01":
                        tc.update({"type": "multicast"})
                    elif tc["mac"].split("-")[0] == "FF":
                        tc.update({"type": "broadcast"})
                    else:
                        tc.update({"type": re.sub("\[([a-zA-Z0-9]+)\]", "\g<1>", entry[7])})

                elif hp.system == "Linux":
                    # Selecting interface
                    tc.update({"interface": entry[6]})
                    # Selecting type
                    if tc["mac"].split("-")[0] == "01":
                        tc.update({"type": "multicast"})
                    elif tc["mac"].split("-")[0] == "FF":
                        tc.update({"type": "broadcast"})
                    else:
                        tc.update({"type": re.sub("\[([a-zA-Z0-9]+)\]", "\g<1>", entry[4])})
                        tc.update({"type": "ethernet"}) if tc["type"] == "ether" else None

                result.append(tc)

    return result


def find_vendor(macs: str, neigh: list):
    """
    This function searches for the NIC vendors in the IEEE DB
    """
    # local vars
    clean_mac_db = []

    # Creating MAC DB in Python dictionary format
    for entry in macs.splitlines():
        if re.match("^[A-Z0-9]+\-", entry):
            tc = {}
            tc.update({"oui": entry.split(" ")[0]})
            tc.update({"vendor": entry.split("\t\t")[1]})

            clean_mac_db.append(tc)

    # Searching for vendors based on MAC
    for entry in neigh:
        entry.update({"vendor": None})

        if entry["type"] == "ethernet":
            # Subtracting OUI
            mac_query = "-".join(entry["mac"].split("-")[0:3])
            
            for sentry in clean_mac_db:
                if sentry["oui"] == mac_query:
                    entry.update({"vendor": sentry["vendor"]})

    return neigh


# Body
if __name__ == "__main__":
    config = hs.import_config("./config.yml")

    # Get platform details
    host_data = get_host_details()

    # Get arguments
    args = args_parser()

    # Timestamping
    t1 = datetime.datetime.now()
    print(f"Starting validation at {t1}...")

    # Collecting info about live hosts
    if args.mode == "remote":
        live_hosts = awake_neighbors(args.targets, args.mode)

    else: 
        live_hosts = awake_neighbors(host_data["ipv4_addresses"], args.mode)

        if args.detailed:
            macdb = get_file(url=config["urls"]["mac_db"], rdir=config["paths"]["cache"])
            live_hosts = get_neighbors(host_data["hp"])
            live_hosts = find_vendor(macs=macdb, neigh=live_hosts)

    # Results
    print(f"\nValidation completed in {datetime.datetime.now() - t1}.\n\nAmount of live hosts: {len(live_hosts)}\n\nDetails:")
    print(json.dumps(live_hosts, indent=4))