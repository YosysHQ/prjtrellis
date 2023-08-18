from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="GLB_ENTRY", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap.ncl",
                          tiles=["CENTER15:CENTER_EBR_CIB_10K", "CENTER8:CENTER_EBR_CIB_SP"]),
        "left_net": "R8C{}_HPSX{:02d}00",
        "right_net": "R8C{}_HPSX{:02d}00"
    },
]


def main():
    def left_end(x):
        if x == 0 or x == 4:
            return 14
        else:
            return 13
        
    def right_end(x):
        if x == 0 or x == 4:
            return 38
        elif x == 1 or x == 5:
            return 36
        else:
            return 37

    pytrellis.load_database("../../../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()
        netnames = []
        netnames += [job["left_net"].format(left_end(x), x) for x in range(8)]
        netnames += [job["right_net"].format(right_end(x), x) for x in range(8)]

        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False)


if __name__ == "__main__":
    main()
