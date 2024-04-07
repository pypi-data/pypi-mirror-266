import os
import subprocess
import argparse
import version

"""
检查当前版本
- 若在可用版本中，有比当前版本更高的版本，则更新到可以获取到的最新版本。
"""

out_parser = argparse.ArgumentParser(description='check_version_and_update')
out_parser.add_argument('--package_name', type=str, required=True)
out_parser.add_argument('--cur_version', type=str, required=False)
out_parser.add_argument('--available_versions', nargs='+', type=str, required=False)
out_parser.add_argument('--verbose', type=int, required=False, default=1)
args = out_parser.parse_args().__dict__

# try to read cur_version
if args["cur_version"] is None:
    ex = subprocess.Popen(f'pip list | grep "{args["package_name"]} "', shell=True, stdout=subprocess.PIPE)
    out, _ = ex.communicate()
    out = out.decode().strip()
    # breakpoint()
    args["cur_version"] = out.split(args["package_name"])[-1].strip()

# try to read available versions
if args["available_versions"] is None:
    ex = subprocess.Popen(f'pip install {args["package_name"]}==?', shell=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    out, _ = ex.communicate()
    out = out.decode().strip()
    if "(from versions:" in out:
        v_ls = out.split("(from versions:")[-1].rsplit(")", 1)[0].split(",", -1)
        v_ls = [i.strip() for i in v_ls]
    else:
        v_ls = ["none"]
    args["available_versions"] = version.sort_ls(version_ls=v_ls, reverse=True)

if len(args["available_versions"]) > 0 and version.compare(args["available_versions"][0], ">", args["cur_version"]):
    ex = subprocess.Popen(
        f'pip install {args["package_name"]}=={args["available_versions"][0]} --no-dependencies',
        shell=True, stdout=subprocess.PIPE
    )
    out, _ = ex.communicate()
    res = out.decode().strip()
else:
    res = "Already the latest version, no need to update"

if args["verbose"]:
    # print(args)
    print(res)
