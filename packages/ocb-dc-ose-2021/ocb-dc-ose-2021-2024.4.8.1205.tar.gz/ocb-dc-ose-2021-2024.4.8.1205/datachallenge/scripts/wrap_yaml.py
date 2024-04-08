import argparse
import sys

import yaml

parser = argparse.ArgumentParser(description="wrap yaml in key and dump")
parser.add_argument("--key", type=str, help="wrapping key")


args = parser.parse_args()
d = yaml.safe_load(sys.stdin.read())

yaml.dump({args.key: d}, stream=sys.stdout)
