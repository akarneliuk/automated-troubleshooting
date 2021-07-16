#!/usr/bin/env python

# Modules
import yaml
import subprocess
import sys
import json
import requests
from tqdm import tqdm
import folium
import re
from pyvis.network import Network


# Variables
config_file = "./gconfig.yml"
destination = ("google.com", "ipv6")


# User-defined functions
def get_path(target: str, target_type: str = "ipv4") -> dict:
    """
    This function runs the MTR and collects its output in JSON format
    """
    allowed_types = {"ipv4", "ipv6"}

    if target_type not in allowed_types:
        sys.exit(f"Unsupported path type. Only {', '.join(allowed_types)} are supported.")

    print(f"Tracing the path to {target} over {target_type}...")

    target_type = "-6" if target_type == "ipv6" else "-4"
    args = ["mtr", target_type, target, "-n", "-z", "-j"]

    result_raw = subprocess.run(args=args, capture_output=True)
    
    if not result_raw.stderr:
        result = json.loads(result_raw.stdout.decode("utf-8"))

    else:
        sys.exit(f"There is some error with trace happened: {result_raw.stderr.decode('utf-8')}")

    print("Tracing completed.")

    return result


def augment_geo_data(mtr_result: dict, geo_config: dict) -> dict:
    """
    This function augments the traceroute with the Geo data
    """
    result = mtr_result

    for he in tqdm(result["report"]["hubs"], desc="Collecting Geo data", colour="blue"):
        url = f"{geo_config['geo']['url']}/{he['host']}?access_key={geo_config['geo']['token']}"
        response = requests.get(url=url)

        if response.status_code == 200:
            try:
                he.update({"geo": response.json()})

            except json.decoder.JSONDecodeError as e:
                he.update({"geo": {}})

    return result


def build_map(mtr_result: dict, geo_config: dict) -> None:
    """
    This function builds the map of the trace
    """
    m = folium.Map()

    print("Drawing the map...")
    minus_one_hop = 0
    for index, entry in enumerate(mtr_result["report"]["hubs"]):
        if entry["geo"]:
            folium.Marker(
                location=[entry["geo"]["latitude"], entry["geo"]["longitude"]],
                popup=f"Hop: {entry['count']}<br>IP: {entry['host']}<br>Country: {entry['geo']['country_name']}<br>City: {entry['geo']['city']}<br>ASN: {re.sub('AS', '', entry['ASN'])}",
                icon=folium.Icon(color="red")
            ).add_to(m)

            if index > 0 and mtr_result["report"]["hubs"][minus_one_hop]['geo']:
                folium.PolyLine(
                    locations=[(entry["geo"]["latitude"], entry["geo"]["longitude"]),(mtr_result["report"]["hubs"][minus_one_hop]["geo"]["latitude"], mtr_result["report"]["hubs"][minus_one_hop]["geo"]["longitude"])],
                    popup=f"Hop {entry['count']} -> Hop {mtr_result['report']['hubs'][minus_one_hop]['count']}",
                    color="red", weight=1.5
                ).add_to(m)

                minus_one_hop = index

    m.save(geo_config["result"]["file_map"])


def augment_isp(mtr_result: dict, geo_config: dict) -> dict:
    """
    This function augments the traceroute with ISP information
    """
    result = mtr_result

    for he in tqdm(result["report"]["hubs"], desc="Collecting ISP information", colour="blue"):
        url = f"{geo_config['isp']['url']}/net?asn={re.sub('AS', '', he['ASN'])}"
        response = requests.get(url=url)

        if response.status_code == 200:
            try:
                he.update({"isp": response.json()['data'][0]})

            except json.decoder.JSONDecodeError as e:
                he.update({"isp": {}})

        else:
            he.update({"isp": {}})

    return result


def build_isp(target: str, mtr_result: dict, geo_config: dict) -> None:
    """
    This function builds the map of the trace
    """
    groups = ["You"]

    failure_colors = [
        "#ffffff",
        "#ffeeee",
        "#ffdddd",
        "#ffcccc",
        "#ffbbbb",
        "#ffaaaa",
        "#ff8888",
        "#ff6666",
        "#ff4444",
        "#ff2222",
        "#ff0000"
    ]

    print("Compiling the trace...")

    nt = Network(height="600px", width="1200px", directed=True, bgcolor="#212121", font_color="#ffffff", 
                 layout=True, heading=f"Traceroute to {target[0]} over {target[1]}")
    
    nt.add_node(0, label=mtr_result["report"]["mtr"]["src"], title="You", level=0)

    for he in mtr_result["report"]["hubs"]:
        isp_name = he["isp"]["name"] if he["isp"] else "Unknown ISP"
        asn = int(re.sub('AS', '', he['ASN']))
        title = f"ISP: {isp_name}<br>ASN: {asn}<br>IP: {he['host']}"
        
        if asn not in groups:
            groups.append(he["isp"]["asn"])
            group = len(groups) - 1

        else:
            i = 0
            while he["isp"]["asn"] != groups[i]:
                i += 1

            group = i

        for i, fc in enumerate(failure_colors):
            if he["Loss%"] == float(i * 10):
                lc = fc
            else:
                if he["Loss%"] > float(i * 10) and he["Loss%"] < float((i + 1) * 10):
                    lc = failure_colors[i + 1]
                
        nt.add_node(int(he["count"]), label=he["host"], title=title, level=group)
        nt.add_edge(int(he["count"]) - 1, int(he["count"]), title=f"Loss: {he['Loss%']}%<br>Latency: {he['Avg']} ms", color=lc, weight=1.5)

    nt.show(geo_config["result"]["file_asn"])


# Body
if __name__ == "__main__":
    # Getting config
    try:
        config = yaml.load(open(config_file, "r").read(), Loader=yaml.Loader)

    except:
        sys.exit(f"Can't open the cofniguration file {config_file}.")

    # Geting hops
    traceroute = get_path(*destination)

    if len(sys.argv) < 2 or sys.argv[1] == "map":    
        # Getting geo data
        traceroute = augment_geo_data(traceroute, config)

        # Build map
        build_map(traceroute, config)

    if len(sys.argv) > 1 and sys.argv[1] == "isp":
        # Getting ISP names
        traceroute = augment_isp(traceroute, config)

        # Build map
        build_isp(destination, traceroute, config)