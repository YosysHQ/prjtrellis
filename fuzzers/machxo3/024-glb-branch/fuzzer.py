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
    (FuzzConfig(job="GLB_BRANCH37", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["R5C17:PLC"]), ["R5C18_HPBX0300", "R5C18_HPBX0700"]),
    (FuzzConfig(job="GLB_BRANCH26", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["R5C16:PLC"]), ["R5C17_HPBX0200", "R5C17_HPBX0600"]),
    (FuzzConfig(job="GLB_BRANCH15", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["R5C15:PLC"]), ["R5C16_HPBX0100", "R5C16_HPBX0500"]),
    (FuzzConfig(job="GLB_BRANCH04", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["R5C14:PLC"]), ["R5C15_HPBX0000", "R5C15_HPBX0400"]),

    # CIB_EBR
    (FuzzConfig(job="CIB_EBR_BRANCH26", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C4:CIB_EBR0"]), ["R6C5_HPBX0200", "R6C5_HPBX0600"]),
    (FuzzConfig(job="CIB_EBR_BRANCH15", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C7:CIB_EBR0"]), ["R6C8_HPBX0100", "R6C8_HPBX0500"]),
    (FuzzConfig(job="CIB_EBR_BRANCH04", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C10:CIB_EBR0"]), ["R6C11_HPBX0000", "R6C11_HPBX0400"]),
    (FuzzConfig(job="CIB_EBR_BRANCH37", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C17:CIB_EBR0"]), ["R6C18_HPBX0300", "R6C18_HPBX0700"]),

    # CIB_PIC_T0.
    (FuzzConfig(job="CIB_PIC_T0_BRANCH37", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C9:CIB_PIC_T0"]), ["R1C10_HPBX0300", "R1C10_HPBX0700"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH04", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C10:CIB_PIC_T0"]), ["R1C11_HPBX0000", "R1C11_HPBX0400"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH15", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C11:CIB_PIC_T0"]), ["R1C12_HPBX0100", "R1C12_HPBX0500"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH26", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C12:CIB_PIC_T0"]), ["R1C13_HPBX0200", "R1C13_HPBX0600"]),

    # CIB_EBR0_END0
    (FuzzConfig(job="CIB_EBR0_END0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C1:CIB_EBR0_END0"]), ["R6C1_HPBX0100", "R6C2_HPBX0200", "R6C2_HPBX0300",
                                                          "R6C1_HPBX0500", "R6C2_HPBX0600", "R6C2_HPBX0700"]),

    # PIC_L0
    (FuzzConfig(job="PIC_L0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PL5:PIC_L0"]), ["R5C1_HPBX0100", "R5C2_HPBX0200", "R5C2_HPBX0300",
                                              "R5C1_HPBX0500", "R5C2_HPBX0600", "R5C2_HPBX0700"]),

    # CIB_EBR2_END0- This appears to be a noop after other fuzzers run.
    (FuzzConfig(job="CIB_EBR2_END0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C22:CIB_EBR2_END0"]), ["R6C22_HPBX0000", "R6C22_HPBX0100",
                                                          "R6C22_HPBX0400", "R6C22_HPBX0500"]),

    # PIC_R0- This also appears to be a noop after other fuzzers run.
    (FuzzConfig(job="PIC_R0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PR5:PIC_R0"]), ["R5C22_HPBX0000", "R5C22_HPBX0100",
                                              "R5C22_HPBX0400", "R5C22_HPBX0500"]),

    # URC0- This also appears to be a noop after other fuzzers run.
    (FuzzConfig(job="URC0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PR1:URC0"]), ["R1C22_HPBX0000", "R1C22_HPBX0100",
                                              "R1C22_HPBX0400", "R1C22_HPBX0500"]),

    # LRC0- This also appears to be a noop after other fuzzers run.
    (FuzzConfig(job="LRC0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PR11:LRC0"]), ["R11C22_HPBX0000", "R11C22_HPBX0100",
                                              "R11C22_HPBX0400", "R11C22_HPBX0500"]),

    # ULC0
    (FuzzConfig(job="ULC0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PL1:ULC0"]), ["R1C1_HPBX0100", "R1C2_HPBX0200", "R1C2_HPBX0300",
                                              "R1C1_HPBX0500", "R1C2_HPBX0600", "R1C2_HPBX0700"]),

    # LLC0
    (FuzzConfig(job="LLC0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PL11:LLC0"]), ["R11C1_HPBX0100", "R11C2_HPBX0200", "R11C2_HPBX0300",
                                              "R11C1_HPBX0500", "R11C2_HPBX0600", "R11C2_HPBX0700"]),
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
