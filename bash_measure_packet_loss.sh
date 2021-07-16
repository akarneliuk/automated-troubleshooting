#!/usr/bin/env bash

OUTPUT="results.csv"
INTERVAL="0.1"
COUNT="20"

echo "host_ip,packet_loss" > "${OUTPUT}"

SYSTEM_TYPE=$(uname)

while read LINE; do
    echo "Checking packet loss for ${LINE}..."

    if [[ ${SYSTEM_TYPE} == "Linux" ]]; then
        PACKET_LOSS=$(ping ${LINE} -c ${COUNT} -i ${INTERVAL} | awk '/loss/ {print $6}')

    else
        PACKET_LOSS=$(ping ${LINE} -c ${COUNT} -i ${INTERVAL} | awk '/loss/ {print $7}')

    fi

    echo "${LINE},${PACKET_LOSS}" >> "${OUTPUT}"

done < ${1}