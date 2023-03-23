from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="GLB_ENTRY", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                          tiles=["CENTER6:CENTER_EBR_CIB"]),
        "left_net": "R6C{}_HPSX{:02d}00",
        "right_net": "R6C{}_HPSX{:02d}00"
    },
]


def main():
    # left_end and right_end are 1200HC-specific. However, the results
    # also readily apply to 2000HC devices because they also have a
    # CENTER_EBR_CIB tile (without qualifiers).
    def left_end(x):
        return 8 if x % 2 == 0 else 7

    def right_end(x):
        if x == 0 or x == 4:
            return 18
        elif x == 1 or x == 5:
            return 19
        else:
            return 17

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
