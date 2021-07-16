# Troubleshooting with Python and Bash
Here you can find some Python and Bash scripts aiming to help you with the troubleshooting.

## Index
Script | Description
--- | --- 
 [get_public_ip.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/get_public_ip.py) | Resolving your public IP and printing to stdout
 [get_speed.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/get_speed.py) | Measuring the speed of your internet connectivity and mailing to you. Requires `speedtest` installation at Your Linux/MAC.
 [measure_speed.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/measure_speed.py) | Run the client side of the iperf3 session to a default port and save the output. Executed as `./measure_speed.py iperf3_server_ip`. Add it to cron as: `0 * * * * /home/aaa/Dev/automated-troubleshooting/measure_speed.py 192.168.1.67` in `crontab -e` in CentOS. Requires `iperf3` installation at Your Linux/MAC.
 [get_nodes.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/get_nodes.py) | Generate the list of the hosts live in either your local subnet or in a chosen destination. Requires `fping` installation at Your Linux/MAC.
 [shell_tools.sh](https://github.com/akarneliuk/automated-troubleshooting/blob/main/shell_tools.sh) | Install the necessary tools (e.g., iperf3, fping, etc) at your Operating System
 [bash_cumulus_vxlan.sh](https://github.com/akarneliuk/automated-troubleshooting/blob/main/bash_cumulus_vxlan.sh) | Genrate IP/MAC/VLAN/VTEP mapping for Cumulus Linux
 [bash_measure_packet_loss.sh](https://github.com/akarneliuk/automated-troubleshooting/blob/main/bash_measure_packet_loss.sh) | Measure the packet loss towards the list of destinations

## Want to learn more?
We have something for you:
- [Advanced network automation](https://training.karneliuk.com/forms/) - All you need to know and can about the network automation: XML/JSON/YAML/Protobuf, SSH/NETCONF/RESTCONF/GNMI, Bash/Ansible/Python, and many more.
- [Network automation with Nornir](https://training.karneliuk.com/network-automation-with-nornir/) - Usage of the Nornir for the automation of the networks and not only.

## Release 
Current release is `0.2.2`.

## Applicability
Any *-NIX based system (e.g., Linux, Unix, MAC OS). In fact, those Python scipts perfectly run on Raspbery PI as well (tested at PI 4B).

(c)2020-2021, karneliuk.com