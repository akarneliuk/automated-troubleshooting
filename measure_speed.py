#!/usr/bin/env python

# Modules
import subprocess
import sys
import json
import datetime
import os

# Variables
target_dir = "./reports"

# Body
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Wrong number of arguments is provided.")

    result = json.loads(subprocess.run(["iperf3", "-c", sys.argv[1], '--json'], stdout=subprocess.PIPE).stdout.decode('utf-8'))

    if result:
        day, time = str(datetime.datetime.now()).split(" ")
        tl = time.split(":")
        fn = f"results_{tl[0]}:{tl[1]}.json"

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        if not os.path.exists(f"{target_dir}/{day}"):
            os.mkdir(f"{target_dir}/{day}")

        with open(f"{target_dir}/{day}/{fn}", "w") as f:
            f.write(json.dumps(result, indent=4, sort_keys=True))
