from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="TAP_DRIVE", family="ECP5", device="LFE5U-25F", ncl="tap.ncl",
                          tiles=["TAP_R6C22:TAP_DRIVE"]),
        "left_net": "R6C17_HPBX{:02d}00",
        "right_net": "R6C26_HPBX{:02d}00"
    }
]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()
        netnames = []
        netnames += [job["left_net"].format(x) for x in range(16)]
        netnames += [job["right_net"].format(x) for x in range(16)]

        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False)


if __name__ == "__main__":
    main()
