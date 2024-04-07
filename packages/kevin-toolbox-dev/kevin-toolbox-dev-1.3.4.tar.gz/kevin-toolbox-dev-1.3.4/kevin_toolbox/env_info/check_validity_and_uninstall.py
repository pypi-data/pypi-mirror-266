import os
import subprocess
import argparse
import time

"""
检查包
- 若超过指定的有效期，则卸载。
"""

out_parser = argparse.ArgumentParser(description='check_validity_and_uninstall')
out_parser.add_argument('--package_name', type=str, required=True)
out_parser.add_argument('--expiration_timestamp', type=int, required=False, default=1e10)
out_parser.add_argument('--verbose', type=int, required=False, default=1)
args = out_parser.parse_args().__dict__

cur_timestamp = time.time()

if cur_timestamp > args["expiration_timestamp"]:
    ex = subprocess.Popen(f'pip uninstall {args["package_name"]} --yes', shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out, _ = ex.communicate()
    res = out.decode().strip()
else:
    res = "still within the validity period"

if args["verbose"]:
    # print(args)
    print(res)
