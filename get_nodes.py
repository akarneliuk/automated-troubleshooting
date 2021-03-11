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
    parser.add_argument("--detailed", action="store_true",
                        help="Specify if you want to get detailed info about local neigbors. Works with local.")
    parser.add_argument("--ipv4", action="store_true",
                        help="Specify if you want to check IPv4 reachability.")
    parser.add_argument("--ipv6", action="store_true",
                        help="Specify if you want to check IPv6 reachability.")

    result = parser.parse_args()
    result.targets = result.targets.split(",")

    if result.mode not in {"local", "remote"}:
        sys.exit("Wrong operations mode. Must be local or remote")

    if result.mode == "remote" and not result.targets:
        sys.exit("The remote mode is chosen, but no ranges provided.")

    # Setting default mode to IPv4
    if not result.ipv4 and not result.ipv6:
        result.ipv4 = True

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

    local_networks = []
    tc = None

    raw_data = subprocess.run(["ifconfig"], capture_output=True).stdout.decode("utf-8")
    raw_data = raw_data.splitlines()

    for raw_line in  raw_data:
        if re.match("^\w+?", raw_line):
            if tc:
                local_networks.append(tc)

            tc = {"interface": raw_line.split(":")[0], "ipv4": [], "ipv6": []}

        # Subtracting IPv4 addresses excluding looback
        elif re.match("\s+inet\s+.*", raw_line) and not re.match(".*\s+127\..*", raw_line):
            tip = re.sub("^.+inet\s+([\d\.]+)\s+.*", "\g<1>", raw_line)
            tpx = re.sub("^.+netmask\s+([\w\.]+)\s+.*", "\g<1>", raw_line)

            # Converting Hex to prefix length
            if hp.system == "Darwin":
                tpx = bin(int(tpx, 16))[2:]
            # Converting dotted decial to prefix length
            else:
                tpx = "".join([bin(int(e))[2:] for e in tpx.split(".")])

            tpx = len([elem for elem in tpx if elem == "1"])

            tc["ipv4"].append(f"{tip}/{tpx}")

        # Subtracting IPv6 addresses excluding link-local addresses
        elif re.match("\s+inet6\s+.*", raw_line) and not (re.match(".*\s+fe80:.*", raw_line) or re.match(".*\s+::1\s+.*", raw_line)):
            tip = re.sub("^.+inet6\s+([\w:]+)\s+.*", "\g<1>", raw_line)
            tpx = re.sub("^.+prefixlen\s+([\d]+)\s+.*", "\g<1>", raw_line)

            tc["ipv6"].append(f"{tip}/{tpx}")

    result = {"hp": hp, "hostname": hostname, "networks": local_networks}

    return result


def awake_neighbors(ip_list: list, args):
    """
    This functions runs fping for the connected subnets to force hosts to appear
    in ARP table
    """
    # Local vars
    result = []
    restructured_ip_list = {"ipv4": [], "ipv6": []}

    # Adding the prefix (default assumption that prefix is /24)
    if args.mode == "local":
        for entry in ip_list:
            restructured_ip_list["ipv4"].extend(entry["ipv4"])
            restructured_ip_list["ipv6"].extend(entry["ipv6"])

    else:
        for entry in ip_list:
            if re.match("\d+\.\d+\.\d+\.\d+/\d+", entry):
                restructured_ip_list["ipv4"].append(entry)

            elif re.match("[0-9A-Fa-f:]+?/*d*", entry):
                restructured_ip_list["ipv6"].append(entry)

    # Validating the reachebility of IPV4 host
    if args.ipv4:
        for entry in restructured_ip_list["ipv4"]:
            raw_data = subprocess.run(["fping", "-4", "-g", entry, "-a", "-q"], capture_output=True).stdout.decode("utf-8")
            result.extend(raw_data.splitlines())

    # Validating the reachebility of IPV6 host
    if args.ipv6:
        for entry in restructured_ip_list["ipv6"]:
            raw_data = subprocess.run(["fping", "-6", entry, "-a", "-q"], capture_output=True).stdout.decode("utf-8")
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
        live_hosts = awake_neighbors(args.targets, args)

    else: 
        live_hosts = awake_neighbors(host_data["networks"], args)

        if args.detailed:
            macdb = get_file(url=config["urls"]["mac_db"], rdir=config["paths"]["cache"])
            live_hosts = get_neighbors(host_data["hp"])
            live_hosts = find_vendor(macs=macdb, neigh=live_hosts)

    # Results
    print(f"\nValidation completed in {datetime.datetime.now() - t1}.\n\nAmount of live hosts: {len(live_hosts)}\n\nDetails:")
    print(json.dumps(live_hosts, indent=4))