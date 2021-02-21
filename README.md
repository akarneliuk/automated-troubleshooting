# Troubleshooting with Python
Here you can find some Python scripts aiming to help you with the troubleshooting.

## Index
Script | Description
--- | --- 
 [get_public_ip.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/get_public_ip.py) | Resolving your public IP and printing to stdout
 [get_speed.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/get_speed.py) | Measuring the speed of your internet connectivity and mailing to you. Requires speedtest installation.
 [measure_speed.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/measure_speed.py) | Run the client side of the iperf3 session to a default port and save the output. Executed as `./measure_speed.py iperf3_server_ip`. Add it to cron as: `0 * * * * /home/aaa/Dev/automated-troubleshooting/measure_speed.py 192.168.1.67` in `crontab -e` in CentOS. Requires iperf3 installation.
 [get_nodes.py](https://github.com/akarneliuk/automated-troubleshooting/blob/main/get_nodes.py) | Generate the list of the hosts live in either your local subnet or in a chosen destination. Requires fping installation.

## Want to learn more?
We have something for you:
- [Advanced network automation](https://training.karneliuk.com/forms/) - All you need to know and can about the network automation: XML/JSON/YAML/Protobuf, SSH/NETCONF/RESTCONF/GNMI, Bash/Ansible/Python, and many more.
- [Network automation with Nornir](https://training.karneliuk.com/network-automation-with-nornir/) - Usage of the Nornir for the automation of the networks and not only.

## Release 
Current release is `0.1.1`.

## Applicability
Any *-NIX based system (e.g., Linux, Unix, MAC OS). In fact, those Python scipts perfectly run on Raspbery PI as well (tested at PI 4B).

(c)2020-2021, karneliuk.com