#!/usr/bin/env python3


# Ref: https://github.com/netdata/netdata/pull/12847
def get_zfs_shrinkable_cache_size_bytes():
    size = 0
    c_min = 0
    with open("/proc/spl/kstat/zfs/arcstats") as f:
        for line in f:
            fields = line.split()
            if line.startswith("size "):
                size = int(fields[2])
            elif line.startswith("c_min "):
                c_min = int(fields[2])
    return max(size - c_min, 0)

def main():
    meminfo = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            value = value.strip()
            if value.endswith("kB"):
                value = value.removesuffix(" kB")
                value = 1024 * int(value)
            else:
                value = int(value)
            meminfo[key] = value
    # Match https://github.com/influxdata/telegraf/blob/5cb142e67631a2dae1cdb30e6909da92e17d1431/plugins/inputs/mem/mem.go#L65-L94
    fields = {}
    fields["total"] = meminfo["MemTotal"]
    fields["available"] = meminfo["MemAvailable"]
    fields["used"] = meminfo["MemTotal"] - meminfo["MemFree"] - meminfo["Buffers"] - meminfo["Cached"]
    fields["active"] = meminfo["Active"]
    fields["buffered"] = meminfo["Buffers"]
    fields["cached"] = meminfo["Cached"]
    fields["commit_limit"] = meminfo["CommitLimit"]
    fields["committed_as"] = meminfo["Committed_AS"]
    fields["dirty"] = meminfo["Dirty"]
    fields["free"] = meminfo["MemFree"]
    fields["high_free"] = meminfo.get("HighFree", 0)
    fields["high_total"] = meminfo.get("HighTotal", 0)
    fields["huge_pages_free"] = meminfo["HugePages_Free"]
    fields["huge_page_size"] = meminfo["Hugepagesize"]
    fields["huge_pages_total"] = meminfo["HugePages_Total"]
    fields["inactive"] = meminfo["Inactive"]
    fields["low_free"] = meminfo.get("LowFree", 0)
    fields["low_total"] = meminfo.get("LowTotal", 0)
    fields["mapped"] = meminfo["Mapped"]
    fields["page_tables"] = meminfo["PageTables"]
    fields["shared"] = meminfo["Shmem"]
    fields["slab"] = meminfo["Slab"]
    fields["sreclaimable"] = meminfo["SReclaimable"]
    fields["sunreclaim"] = meminfo["SUnreclaim"]
    fields["swap_cached"] = meminfo["SwapCached"]
    fields["swap_free"] = meminfo["SwapFree"]
    fields["swap_total"] = meminfo["SwapTotal"]
    fields["vmalloc_chunk"] = meminfo["VmallocChunk"]
    fields["vmalloc_total"] = meminfo["VmallocTotal"]
    fields["vmalloc_used"] = meminfo["VmallocUsed"]
    fields["write_back_tmp"] = meminfo["WritebackTmp"]
    fields["write_back"] = meminfo["Writeback"]

    zfs_arc_shrinkable_size = get_zfs_shrinkable_cache_size_bytes()
    fields["used"] -= zfs_arc_shrinkable_size
    fields["cached"] += zfs_arc_shrinkable_size
    fields["available"] += zfs_arc_shrinkable_size
    fields["used_percent"] = 100 * fields["used"] / fields["total"]
    fields["available_percent"] = 100 * fields["available"] / fields["total"]

    print("mem ", end="")
    for idx, key in enumerate(fields):
        print(f"{key}={fields[key]}", end="")
        if type(fields[key]) is int:
            print("i", end="")
        if idx != len(fields) - 1:
            print(",", end="")
    print()

if __name__ == "__main__":
    main()
