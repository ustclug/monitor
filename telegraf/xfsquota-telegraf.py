#!/usr/bin/env python3

import argparse
import subprocess as sp


def main():
    command = ["/sbin/xfs_quota", "-c", "free -N"]
    ret = sp.run(command, stdout=sp.PIPE)
    if ret.returncode != 0:
        raise RuntimeError(f"xfs_quota failed with return value {ret.returncode}")
    # parse xfs_quota output
    # the output of one path may not on one single line
    # so I have to use this dirty way to parse it
    i = 0
    lines = ret.stdout.decode('utf8').strip().split('\n')
    data = {}
    while i < len(lines):
        line = lines[i]
        splits = line.split()
        i += 1
        if len(splits) < 6:
            assert i < len(lines)
            line += lines[i]
            splits = line.split()
            i += 1
        assert len(splits) == 6
        fs, onekblk, used, available, _, path = splits
        data[path] = {
            "fs": fs,
            "1kblk": onekblk,
            "used": used,
            "available": available,
        }
    # produce influxdb format
    for path, info in data.items():
        print(f"xfsquota,path={path} fs=\"{info['fs']}\",onekblk={info['1kblk']},used={info['used']},available={info['available']}")

if __name__ == "__main__":
    main()

