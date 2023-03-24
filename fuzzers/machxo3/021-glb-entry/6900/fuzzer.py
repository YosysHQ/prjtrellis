from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="GLB_ENTRY", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap.ncl",
                          tiles=["CENTER13:CENTER_EBR_CIB_4K"]),
        "left_net": "R13C{}_HPSX{:02d}00",
        "right_net": "R13C{}_HPSX{:02d}00"
    },
]


def main():
    def left_end(x): 
        if x == 2 or x == 3 or x == 6 or x == 7:
            return 11
        else:
            return 10

    def right_end(x):
        if x == 3 or x == 7:
            return 29
        else:
            return 30

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
