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
    # PLC
    (FuzzConfig(job="GLB_BRANCH37", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C17:PLC"]), ["R5C18_HPBX0300", "R5C18_HPBX0700"]),
    (FuzzConfig(job="GLB_BRANCH26", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C16:PLC"]), ["R5C17_HPBX0200", "R5C17_HPBX0600"]),
    (FuzzConfig(job="GLB_BRANCH15", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C15:PLC"]), ["R5C16_HPBX0100", "R5C16_HPBX0500"]),
    (FuzzConfig(job="GLB_BRANCH04", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["R5C14:PLC"]), ["R5C15_HPBX0000", "R5C15_HPBX0400"]),

    # CIB_EBR
    (FuzzConfig(job="CIB_EBR_BRANCH26", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C4:CIB_EBR0"]), ["R6C5_HPBX0200", "R6C5_HPBX0600"]),
    (FuzzConfig(job="CIB_EBR_BRANCH15", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C7:CIB_EBR0"]), ["R6C8_HPBX0100", "R6C8_HPBX0500"]),
    (FuzzConfig(job="CIB_EBR_BRANCH04", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C10:CIB_EBR0"]), ["R6C11_HPBX0000", "R6C11_HPBX0400"]),
    (FuzzConfig(job="CIB_EBR_BRANCH37", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C17:CIB_EBR0"]), ["R6C18_HPBX0300", "R6C18_HPBX0700"]),

    # CIB_EBR0_END0
    (FuzzConfig(job="CIB_EBR0_END0_BRANCH", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C1:CIB_EBR0_END0"]), ["R6C1_HPBX0100", "R6C2_HPBX0200", "R6C2_HPBX0300",
                                                          "R6C1_HPBX0500", "R6C2_HPBX0600", "R6C2_HPBX0700"]),

    # PIC_L0
    (FuzzConfig(job="PIC_L0_BRANCH", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["PL5:PIC_L0"]), ["R5C1_HPBX0100", "R5C2_HPBX0200", "R5C2_HPBX0300",
                                              "R5C1_HPBX0500", "R5C2_HPBX0600", "R5C2_HPBX0700"]),

    # CIB_EBR2_END0- This appears to be a noop after other fuzzers run.
    (FuzzConfig(job="CIB_EBR2_END0_BRANCH", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C22:CIB_EBR2_END0"]), ["R6C22_HPBX0000", "R6C22_HPBX0100",
                                                          "R6C22_HPBX0400", "R6C22_HPBX0500"]),
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
