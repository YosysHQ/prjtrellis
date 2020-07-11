from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import argparse
from nets import net_product

# def mk_nets(tilepos, glb_ids):
#     branch_nets = []
#     rc_prefix = "R{}C{}_".format(tilepos[0], tilepos[1])
#
#     # Branch Conns... will be
#     branch_nets.extend(net_product([rc_prefix + "HPBX0{}00"], glb_ids))
#     return branch_nets

jobs = [
    (FuzzConfig(job="GLB_BRANCH37", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C17:PLC"]), ["R5C18_HPBX0300", "R5C18_HPBX0700"]),
    (FuzzConfig(job="GLB_BRANCH26", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C16:PLC"]), ["R5C17_HPBX0200", "R5C17_HPBX0600"]),
    (FuzzConfig(job="GLB_BRANCH15", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C15:PLC"]), ["R5C16_HPBX0100", "R5C16_HPBX0500"]),
    (FuzzConfig(job="GLB_BRANCH04", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C14:PLC"]), ["R5C15_HPBX0000", "R5C15_HPBX0400"]),
]

def main(args):
    pytrellis.load_database("../../../database")

    for job in [jobs[i] for i in args.ids]:
        cfg, netnames = job
        cfg.setup()
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Center Mux Routing Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
