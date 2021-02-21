#(c)2019-2021, karneliuk.com

"""
This module contains the functions shared across multiple tools.
"""

# Modules
import yaml
import sys

# Used-defined functions
def import_config(path: str):
    try:
        with open(path, "r") as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)
        return result
        
    except FileNotFoundError:
        sys.exit(f"The configuration file {path} cannot be found. Check if it exists in your folder.")

