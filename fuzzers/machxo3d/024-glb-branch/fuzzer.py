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
    (FuzzConfig(job="GLB_BRANCH37", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["R5C17:PLC"]), ["R5C18_HPBX0300", "R5C18_HPBX0700"]),
    (FuzzConfig(job="GLB_BRANCH26", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["R5C16:PLC"]), ["R5C17_HPBX0200", "R5C17_HPBX0600"]),
    (FuzzConfig(job="GLB_BRANCH15", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["R5C15:PLC"]), ["R5C16_HPBX0100", "R5C16_HPBX0500"]),
    (FuzzConfig(job="GLB_BRANCH04", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["R5C14:PLC"]), ["R5C15_HPBX0000", "R5C15_HPBX0400"]),

    #4
    # CIB_EBR
    (FuzzConfig(job="CIB_EBR_BRANCH26", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C4:CIB_EBR0"]), ["R8C5_HPBX0200", "R8C5_HPBX0600"]),
    (FuzzConfig(job="CIB_EBR_BRANCH15", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C7:CIB_EBR0"]), ["R8C8_HPBX0100", "R8C8_HPBX0500"]),
    (FuzzConfig(job="CIB_EBR_BRANCH04", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C10:CIB_EBR0"]), ["R8C11_HPBX0000", "R8C11_HPBX0400"]),
    (FuzzConfig(job="CIB_EBR_BRANCH37", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C13:CIB_EBR0"]), ["R8C14_HPBX0300", "R8C14_HPBX0700"]),

    #8
    # CIB_PIC_T0
    (FuzzConfig(job="CIB_PIC_T0_BRANCH37", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R1C9:CIB_PIC_T0"]), ["R1C10_HPBX0300", "R1C10_HPBX0700"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH04", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R1C10:CIB_PIC_T0"]), ["R1C11_HPBX0000", "R1C11_HPBX0400"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH15", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R1C11:CIB_PIC_T0"]), ["R1C12_HPBX0100", "R1C12_HPBX0500"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH26", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R1C12:CIB_PIC_T0"]), ["R1C13_HPBX0200", "R1C13_HPBX0600"]),

    #12
    # CIB_PIC_B0
    (FuzzConfig(job="CIB_PIC_B0_BRANCH37", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R30C5:CIB_PIC_B0"]), ["R30C6_HPBX0300", "R30C6_HPBX0700"]),
    (FuzzConfig(job="CIB_PIC_B0_BRANCH15", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R30C7:CIB_PIC_B0"]), ["R30C8_HPBX0100", "R30C8_HPBX0500"]),
    (FuzzConfig(job="CIB_PIC_B0_BRANCH26", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R30C8:CIB_PIC_B0"]), ["R30C9_HPBX0200", "R30C9_HPBX0600"]),
    (FuzzConfig(job="CIB_PIC_B0_BRANCH04", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["CIB_R30C10:CIB_PIC_B0"]), ["R30C11_HPBX0000", "R30C11_HPBX0400"]),

    #16
    # CIB_EBR_10K
    (FuzzConfig(job="CIB_EBR_10K_BRANCH26", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C4:CIB_EBR0_10K"]), ["R15C5_HPBX0200", "R15C5_HPBX0600"]),
    (FuzzConfig(job="CIB_EBR_10K_BRANCH15", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C7:CIB_EBR0_10K"]), ["R15C8_HPBX0100", "R15C8_HPBX0500"]),
    (FuzzConfig(job="CIB_EBR_10K_BRANCH04", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C10:CIB_EBR0_10K"]), ["R15C11_HPBX0000", "R15C11_HPBX0400"]),
    (FuzzConfig(job="CIB_EBR_10K_BRANCH37", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C13:CIB_EBR0_10K"]), ["R15C14_HPBX0300", "R15C14_HPBX0700"]),


    #20
    # CIB_EBR2_END1 - R - 4300D
    (FuzzConfig(job="CIB_EBR2_END1_BRANCH", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap_4300.ncl",
                      tiles=["R11C33:CIB_EBR2_END1"]), ["R11C32_HPBX0000", "R11C32_HPBX0300",
                                                        "R11C32_HPBX0400", "R11C32_HPBX0700"]),
    # CIB_EBR2_END1_SP - R -  9400
    (FuzzConfig(job="CIB_EBR2_END1_SP_BRANCH", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C49:CIB_EBR2_END1_SP"]), ["R8C49_HPBX0000", "R8C49_HPBX0300",
                                                              "R8C49_HPBX0400", "R8C49_HPBX0700"]),
    # CIB_EBR0_END0_DLL5 - L - 9400
    (FuzzConfig(job="CIB_EBR0_END0_DLL5_BRANCH", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C1:CIB_EBR0_END0_DLL5"]), ["R8C1_HPBX0100", "R8C2_HPBX0200", "R8C2_HPBX0300",
                                                               "R8C1_HPBX0500", "R8C2_HPBX0600", "R8C2_HPBX0700"]),
    # CIB_EBR0_END0_DLL3 - L - 9400
    (FuzzConfig(job="CIB_EBR0_END0_DLL3_BRANCH", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R22C1:CIB_EBR0_END0_DLL3"]), ["R22C1_HPBX0100", "R22C2_HPBX0200", "R22C2_HPBX0300",
                                                                "R22C1_HPBX0500", "R22C2_HPBX0600", "R22C2_HPBX0700"]),
    #24
    # CIB_EBR0_END1 - L - 4300 
    (FuzzConfig(job="CIB_EBR0_END1_BRANCH", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap_4300.ncl",
                      tiles=["CIB_R11C1:CIB_EBR0_END1"]), ["R11C2_HPBX0000", "R11C1_HPBX0200", "R11C2_HPBX0300",
                                                           "R11C2_HPBX0400", "R11C1_HPBX0600", "R11C2_HPBX0700"]),
    # CIB_EBR0_END0_10K - L - 9400
    (FuzzConfig(job="CIB_EBR0_END0_10K_BRANCH", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C1:CIB_EBR0_END0_10K"]), ["R15C1_HPBX0100", "R15C2_HPBX0200", "R15C2_HPBX0300",
                                                               "R15C1_HPBX0500", "R15C2_HPBX0600", "R15C2_HPBX0700"]),
    # CIB_EBR2_END1_10K - R - 9400
    (FuzzConfig(job="CIB_EBR2_END1_10K_BRANCH", family="MachXO3D", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C49:CIB_EBR2_END1_10K"]), ["R15C49_HPBX0000", "R15C49_HPBX0300",
                                                                "R15C49_HPBX0400", "R15C49_HPBX0700",]),

    # This also appears to be a noop after other fuzzers run.
    # PIC_L0
    (FuzzConfig(job="PIC_L0_BRANCH", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["PL5:PIC_L0"]), ["R5C1_HPBX0100", "R5C2_HPBX0200", "R5C2_HPBX0300",
                                              "R5C1_HPBX0500", "R5C2_HPBX0600", "R5C2_HPBX0700"]),

    #28
    # PIC_R1
    (FuzzConfig(job="PIC_R1_BRANCH", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["PR5:PIC_R1"]), ["R5C49_HPBX0000", "R5C49_HPBX0300",
                                              "R5C49_HPBX0400", "R5C49_HPBX0700"]),

    # URC1
    (FuzzConfig(job="URC1_BRANCH", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["PR1:URC1"]), ["R1C49_HPBX0000", "R1C49_HPBX0300",
                                            "R1C49_HPBX0400", "R1C49_HPBX0700",]),

    # LRC1
    (FuzzConfig(job="LRC1_BRANCH", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap_4300.ncl",
                      tiles=["R21C33:LRC1"]), ["R21C32_HPBX0000", "R21C32_HPBX0300",
                                               "R21C32_HPBX0400", "R21C32_HPBX0700"]),

    # LRC1PIC2
    (FuzzConfig(job="LRC1_BRANCH", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["PR30:LRC1PIC2"]), ["R30C49_HPBX0000", "R30C49_HPBX0300",
                                                 "R30C49_HPBX0400", "R30C49_HPBX0700"]),

    #32
    # ULC0
    (FuzzConfig(job="ULC0_BRANCH", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["PL1:ULC0"]), ["R1C1_HPBX0100", "R1C2_HPBX0200", "R1C2_HPBX0300",
                                            "R1C1_HPBX0500", "R1C2_HPBX0600", "R1C2_HPBX0700"]),

    # LLC0PIC_I3C_VREF3 
    (FuzzConfig(job="LLC0_BRANCH", family="MachXO3D", device="LCMXO3D-9400HC", ncl="tap_9400.ncl",
                      tiles=["PL30:LLC0PIC_I3C_VREF3"]), ["R30C1_HPBX0100", "R30C2_HPBX0200", "R30C2_HPBX0300",
                                                          "R30C1_HPBX0500", "R30C2_HPBX0600", "R30C2_HPBX0700"]),

    # PIC_L1
    (FuzzConfig(job="PIC_L1_BRANCH", family="MachXO3D", device="LCMXO3LF-4300E", ncl="tap_4300.ncl",
                      tiles=["PL5:PIC_L1"]), ["R5C2_HPBX0000", "R5C1_HPBX0200", "R5C2_HPBX0300",
                                              "R5C2_HPBX0400", "R5C1_HPBX0600", "R5C2_HPBX0700"]),
    # LLC1
    (FuzzConfig(job="LLC1_BRANCH", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap_4300.ncl",
                      tiles=["PL21:LLC1"]), ["R21C2_HPBX0000", "R21C1_HPBX0200", "R21C2_HPBX0300",
                                             "R21C2_HPBX0400", "R21C1_HPBX0600", "R21C2_HPBX0700"]),
    #36
    # ULC1
    (FuzzConfig(job="ULC1_BRANCH", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap_4300.ncl",
                      tiles=["PL1:ULC1"]), ["R1C2_HPBX0000", "R1C1_HPBX0200", "R1C2_HPBX0300",
                                            "R1C2_HPBX0400", "R1C1_HPBX0600", "R1C2_HPBX0700"]),
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
