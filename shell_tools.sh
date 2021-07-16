#!/usr/bin/env bash

## Tools to install
TOOLS=("speedtest" "iperf3" "fping")

## Taking OS type
OS_TYPE=$(uname)

## Running OS-depndent install
if [[ ${OS_TYPE} == "Linux" ]]; then
    OS_SUBTYPE=$(cat /etc/os-release | awk 'BEGIN {FS="="} /^ID=/ {print $2}' | sed -e 's/"//g')
    OS_VERSION=$(cat /etc/os-release | awk 'BEGIN {FS="="} /^VERSION_ID=/ {print $2}' | sed -e 's/"//g')

    echo "$(date): Starting installation of ${TOOLS[@]} at ${OS_SUBTYPE} ${OS_VERSION}"

    if [[ ${OS_SUBTYPE} == "centos" && ${OS_VERSION} == "8" ]]; then
        sudo dnf -y install ${TOOLS[@]}

    elif [[ ${OS_SUBTYPE} == "centos" && ${OS_VERSION} == "7" ]]; then
        sudo yum -y install ${TOOLS[@]}

    elif [[ ${OS_SUBTYPE} == "ubuntu" || ${OS_SUBTYPE} == "debian" ]]; then
        sudo apt-get -y install ${TOOLS[@]}

    else
        echo "UNSUPPORTED LINUX TYPE"

    fi

elif [[ ${OS_TYPE} == "Darwin" ]]; then
    echo "$(date): Starting installation of ${TOOLS[@]} at ${OS_SUBTYPE} ${OS_VERSION}"
    brew -y install ${TOOLS[@]}

else
    echo "UNSUPPORTED OS TYPE"

fi