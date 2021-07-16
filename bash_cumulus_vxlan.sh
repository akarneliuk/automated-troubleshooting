#!/usr/bin/env bash

OUTPUT="results.csv"

echo "host_ip,host_mac,host_vlan,switch_lo_ip" > "${OUTPUT}"

while read LINE; do
    echo "Looking for destination for ${LINE}..."

    MAC_ANSWER=($(ip -4 neighbor | grep "^${LINE}\s" | awk '{print $5, $3}'))
    SWITCH_IP=$(net show bridge macs | grep "untag.*${MAC_ANSWER[0]}" | awk '{print $4}')

    echo "${LINE},${MAC_ANSWER[0]},${MAC_ANSWER[1]},${SWITCH_IP}" >> "${OUTPUT}"

done < ${1}