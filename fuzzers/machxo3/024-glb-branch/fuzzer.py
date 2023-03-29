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

    #4
    # CIB_EBR
    (FuzzConfig(job="CIB_EBR_BRANCH26", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C4:CIB_EBR0"]), ["R6C5_HPBX0200", "R6C5_HPBX0600"]),
    (FuzzConfig(job="CIB_EBR_BRANCH15", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C7:CIB_EBR0"]), ["R6C8_HPBX0100", "R6C8_HPBX0500"]),
    (FuzzConfig(job="CIB_EBR_BRANCH04", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C10:CIB_EBR0"]), ["R6C11_HPBX0000", "R6C11_HPBX0400"]),
    (FuzzConfig(job="CIB_EBR_BRANCH37", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C17:CIB_EBR0"]), ["R6C18_HPBX0300", "R6C18_HPBX0700"]),

    #8
    # CIB_PIC_T0
    (FuzzConfig(job="CIB_PIC_T0_BRANCH37", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C9:CIB_PIC_T0"]), ["R1C10_HPBX0300", "R1C10_HPBX0700"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH04", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C10:CIB_PIC_T0"]), ["R1C11_HPBX0000", "R1C11_HPBX0400"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH15", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C11:CIB_PIC_T0"]), ["R1C12_HPBX0100", "R1C12_HPBX0500"]),
    (FuzzConfig(job="CIB_PIC_T0_BRANCH26", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R1C12:CIB_PIC_T0"]), ["R1C13_HPBX0200", "R1C13_HPBX0600"]),

    #12
    # CIB_EBR0_END0 - L - 1300
    (FuzzConfig(job="CIB_EBR0_END0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C1:CIB_EBR0_END0"]), ["R6C1_HPBX0100", "R6C2_HPBX0200", "R6C2_HPBX0300",
                                                          "R6C1_HPBX0500", "R6C2_HPBX0600", "R6C2_HPBX0700"]),
    # CIB_EBR2_END0 - R - 1300
    (FuzzConfig(job="CIB_EBR2_END0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R6C22:CIB_EBR2_END0"]), ["R6C22_HPBX0000", "R6C22_HPBX0100",
                                                           "R6C22_HPBX0400", "R6C22_HPBX0500"]),
    # CIB_EBR0_END2_DLL45 - L - 6900
    (FuzzConfig(job="CIB_EBR0_END2_DLL45_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["CIB_R13C1:CIB_EBR0_END2_DLL45"]), ["R13C2_HPBX0000", "R13C2_HPBX0100", "R13C1_HPBX0300",
                                                                 "R13C2_HPBX0400", "R13C2_HPBX0500", "R13C1_HPBX0700"]),
    # CIB_EBR2_END1 - R - 2100, 4300 (same as 2100), 6900
    (FuzzConfig(job="CIB_EBR2_END1_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["CIB_R13C41:CIB_EBR2_END1"]), ["R13C41_HPBX0100", "R13C41_HPBX0200",
                                                            "R13C41_HPBX0500", "R13C41_HPBX0600",]),
    #16
    (FuzzConfig(job="CIB_EBR2_END1_2100_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["CIB_R8C26:CIB_EBR2_END1"]), ["R8C26_HPBX0000", "R8C26_HPBX0300",
                                                           "R8C26_HPBX0400", "R8C26_HPBX0700"]),
    # CIB_EBR0_END2_DLL3 - L - 6900
    (FuzzConfig(job="CIB_EBR0_END2_DLL3_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["CIB_R20C1:CIB_EBR0_END2_DLL3"]), ["R20C2_HPBX0000", "R20C2_HPBX0100", "R20C1_HPBX0300",
                                                                "R20C2_HPBX0400", "R20C2_HPBX0500", "R20C1_HPBX0700"]),

    # CIB_EBR2_END1_SP - R - 6900, 9400
    (FuzzConfig(job="CIB_EBR2_END1_SP_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["CIB_R20C41:CIB_EBR2_END1_SP"]), ["R20C41_HPBX0100", "R20C41_HPBX0200",
                                                               "R20C41_HPBX0500", "R20C41_HPBX0600",]),
    (FuzzConfig(job="CIB_EBR2_END1_SP_9400_BRANCH", family="MachXO3", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C49:CIB_EBR2_END1_SP"]), ["R8C49_HPBX0000", "R8C49_HPBX0300",
                                                              "R8C49_HPBX0400", "R8C49_HPBX0700"]),
    #20
    # CIB_EBR0_END0_DLL5 - L - 9400
    (FuzzConfig(job="CIB_EBR0_END0_DLL5_BRANCH", family="MachXO3", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R8C1:CIB_EBR0_END0_DLL5"]), ["R8C1_HPBX0100", "R8C2_HPBX0200", "R8C2_HPBX0300",
                                                               "R8C1_HPBX0500", "R8C2_HPBX0600", "R8C2_HPBX0700"]),
    # CIB_EBR0_END0_DLL3 - L - 9400
    (FuzzConfig(job="CIB_EBR0_END0_DLL3_BRANCH", family="MachXO3", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R22C1:CIB_EBR0_END0_DLL3"]), ["R22C1_HPBX0100", "R22C2_HPBX0200", "R22C2_HPBX0300",
                                                                "R22C1_HPBX0500", "R22C2_HPBX0600", "R22C2_HPBX0700"]),
    # CIB_EBR_DUMMY_END3 - L - 2100
    (FuzzConfig(job="CIB_EBR_DUMMY_END3_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["CIB_R8C1:CIB_EBR_DUMMY_END3"]), ["R8C1_HPBX0000", "R8C2_HPBX0100", "R8C2_HPBX0200",
                                                               "R8C1_HPBX0400", "R8C2_HPBX0500", "R8C2_HPBX0600"]),
    # CIB_EBR0_END1 - L - 4300 
    (FuzzConfig(job="CIB_EBR0_END1_BRANCH", family="MachXO3", device="LCMXO3LF-4300C", ncl="tap_4300.ncl",
                      tiles=["CIB_R11C1:CIB_EBR0_END1"]), ["R11C2_HPBX0000", "R11C1_HPBX0200", "R11C2_HPBX0300",
                                                           "R11C2_HPBX0400", "R11C1_HPBX0600", "R11C2_HPBX0700"]),
    #24
    # CIB_EBR0_END0_10K - L - 9400
    (FuzzConfig(job="CIB_EBR0_END0_10K_BRANCH", family="MachXO3", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C1:CIB_EBR0_END0_10K"]), ["R15C1_HPBX0100", "R15C2_HPBX0200", "R15C2_HPBX0300",
                                                               "R15C1_HPBX0500", "R15C2_HPBX0600", "R15C2_HPBX0700"]),
    # CIB_EBR2_END1_10K - R - 9400
    (FuzzConfig(job="CIB_EBR2_END1_10K_BRANCH", family="MachXO3", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["CIB_R15C49:CIB_EBR2_END1_10K"]), ["R15C49_HPBX0000", "R15C49_HPBX0300",
                                                                "R15C49_HPBX0400", "R15C49_HPBX0700",]),

    # This also appears to be a noop after other fuzzers run.
    # PIC_L0
    (FuzzConfig(job="PIC_L0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PL5:PIC_L0"]), ["R5C1_HPBX0100", "R5C2_HPBX0200", "R5C2_HPBX0300",
                                              "R5C1_HPBX0500", "R5C2_HPBX0600", "R5C2_HPBX0700"]),

    # PIC_R0
    (FuzzConfig(job="PIC_R0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PR5:PIC_R0"]), ["R5C22_HPBX0000", "R5C22_HPBX0100",
                                              "R5C22_HPBX0400", "R5C22_HPBX0500"]),

    #28
    # URC0
    (FuzzConfig(job="URC0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PR1:URC0"]), ["R1C22_HPBX0000", "R1C22_HPBX0100",
                                            "R1C22_HPBX0400", "R1C22_HPBX0500"]),

    # LRC0
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

    #32
    # PIC_LS0
    (FuzzConfig(job="PIC_LS0_BRANCH", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["PL9:PIC_LS0"]), ["R9C1_HPBX0100", "R9C2_HPBX0200", "R9C2_HPBX0300",
                                               "R9C1_HPBX0500", "R9C2_HPBX0600", "R9C2_HPBX0700"]),

    # PIC_RS0
    (FuzzConfig(job="PIC_RS0_BRANCH", family="MachXO3", device="LCMXO3LF-4300E", ncl="tap.ncl",
                      tiles=["PR3:PIC_RS0"]), ["R3C22_HPBX0000", "R3C22_HPBX0100",
                                               "R3C22_HPBX0400", "R3C22_HPBX0500"]),

    # PIC_L1
    (FuzzConfig(job="PIC_L1_BRANCH", family="MachXO3", device="LCMXO3LF-4300E", ncl="tap_4300.ncl",
                      tiles=["PL5:PIC_L1"]), ["R5C2_HPBX0000", "R5C1_HPBX0200", "R5C2_HPBX0300",
                                              "R5C2_HPBX0400", "R5C1_HPBX0600", "R5C2_HPBX0700"]),

    # PIC_R1
    (FuzzConfig(job="PIC_R1_BRANCH", family="MachXO3", device="LCMXO3LF-4300C", ncl="tap_4300.ncl",
                      tiles=["PR5:PIC_R1"]), ["R5C32_HPBX0000", "R5C32_HPBX0300",
                                              "R5C32_HPBX0400", "R5C32_HPBX0700"]),
    #36
    (FuzzConfig(job="PIC_R1_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["PR5:PIC_R1"]), ["R5C41_HPBX0100", "R5C41_HPBX0200",
                                              "R5C41_HPBX0500", "R5C41_HPBX0600"]),

    # PIC_L2
    (FuzzConfig(job="PIC_L2_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["PL5:PIC_L2"]), ["R5C2_HPBX0000", "R5C2_HPBX0100", "R5C1_HPBX0300",
                                              "R5C2_HPBX0400", "R5C2_HPBX0500", "R5C1_HPBX0700"]),

    # PIC_L3
    (FuzzConfig(job="PIC_L3_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["PL4:PIC_L3"]), ["R4C1_HPBX0000", "R4C2_HPBX0100", "R4C2_HPBX0200",
                                              "R4C1_HPBX0400", "R4C2_HPBX0500", "R4C2_HPBX0600"]),

    # LLC0PIC_VREF3
    (FuzzConfig(job="LLC0PIC_VREF3_BRANCH", family="MachXO3", device="LCMXO3LF-9400C", ncl="tap_9400.ncl",
                      tiles=["PL30:LLC0PIC_VREF3"]), ["R30C1_HPBX0100", "R30C2_HPBX0200", "R30C2_HPBX0300",
                                                      "R30C1_HPBX0500", "R30C2_HPBX0600", "R30C2_HPBX0700"]),
    # 40
    # LLC1
    (FuzzConfig(job="LLC1_BRANCH", family="MachXO3", device="LCMXO3LF-4300C", ncl="tap_4300.ncl",
                      tiles=["PL21:LLC1"]), ["R21C2_HPBX0000", "R21C1_HPBX0200", "R21C2_HPBX0300",
                                             "R21C2_HPBX0400", "R21C1_HPBX0600", "R21C2_HPBX0700"]),
    # LLC2
    (FuzzConfig(job="LLC2_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["PL26:LLC2"]), ["R26C2_HPBX0000", "R26C2_HPBX0100", "R26C1_HPBX0300",
                                             "R26C2_HPBX0400", "R26C2_HPBX0500", "R26C1_HPBX0700"]),

    # LLC3PIC_VREF3
    (FuzzConfig(job="LLC3PIC_VREF3_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["PL14:LLC3PIC_VREF3"]), ["R14C1_HPBX0000", "R14C2_HPBX0100", "R14C2_HPBX0200",
                                                      "R14C1_HPBX0400", "R14C2_HPBX0500", "R14C2_HPBX0600"]),

    # ULC1
    (FuzzConfig(job="ULC1_BRANCH", family="MachXO3", device="LCMXO3LF-4300C", ncl="tap_4300.ncl",
                      tiles=["PL1:ULC1"]), ["R1C2_HPBX0000", "R1C1_HPBX0200", "R1C2_HPBX0300",
                                            "R1C2_HPBX0400", "R1C1_HPBX0600", "R1C2_HPBX0700"]),
    #44
    # ULC2
    (FuzzConfig(job="ULC2_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["PL1:ULC2"]), ["R1C2_HPBX0000", "R1C2_HPBX0100", "R1C1_HPBX0300",
                                            "R1C2_HPBX0400", "R1C2_HPBX0500", "R1C1_HPBX0700"]),
    # ULC3PIC
    (FuzzConfig(job="ULC3PIC_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["PL1:ULC3PIC"]), ["R1C1_HPBX0000", "R1C2_HPBX0100", "R1C2_HPBX0200",
                                               "R1C1_HPBX0400", "R1C2_HPBX0500", "R1C2_HPBX0600"]),

    # LRC1
    (FuzzConfig(job="LRC1_BRANCH", family="MachXO3", device="LCMXO3LF-4300C", ncl="tap_4300.ncl",
                      tiles=["PR21:LRC1"]), ["R21C32_HPBX0000", "R21C32_HPBX0300",
                                             "R21C32_HPBX0400", "R21C32_HPBX0700"]),

    (FuzzConfig(job="LRC1_BRANCH", family="MachXO3", device="LCMXO3LF-6900C", ncl="tap_6900.ncl",
                      tiles=["PR26:LRC1"]), ["R26C41_HPBX0100", "R26C41_HPBX0200",
                                             "R26C41_HPBX0500", "R26C41_HPBX0600"]),
    #48
    # LRC1PIC2 same for 9400 and 2100
    (FuzzConfig(job="LRC1PIC2_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["PR14:LRC1PIC2"]), ["R14C26_HPBX0000", "R14C26_HPBX0300",
                                                 "R14C26_HPBX0400", "R14C26_HPBX0700"]),

    # URC1 same for 4300 and 6900
    (FuzzConfig(job="URC1_BRANCH", family="MachXO3", device="LCMXO3LF-4300C", ncl="tap_4300.ncl",
                      tiles=["PR1:URC1"]), ["R1C32_HPBX0000", "R1C32_HPBX0300",
                                            "R1C32_HPBX0400", "R1C32_HPBX0700"]),

    # URC1PIC
    (FuzzConfig(job="URC1PIC_BRANCH", family="MachXO3", device="LCMXO3LF-2100C", ncl="tap_2100.ncl",
                      tiles=["PR1:URC1PIC"]), ["R1C26_HPBX0000", "R1C26_HPBX0300",
                                               "R1C26_HPBX0400", "R1C26_HPBX0700"]),

    #51
    # CIB_PIC_B0
    (FuzzConfig(job="CIB_PIC_B0_BRANCH26", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R11C4:CIB_PIC_B0"]), ["R11C5_HPBX0200", "R11C5_HPBX0600"]),
    (FuzzConfig(job="CIB_PIC_B0_BRANCH04", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R11C6:CIB_PIC_B0"]), ["R11C7_HPBX0000", "R11C7_HPBX0400"]),
    (FuzzConfig(job="CIB_PIC_B0_BRANCH37", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R11C9:CIB_PIC_B0"]), ["R11C10_HPBX0300", "R11C10_HPBX0700"]),
    (FuzzConfig(job="CIB_PIC_B0_BRANCH15", family="MachXO3", device="LCMXO3LF-1300E", ncl="tap.ncl",
                      tiles=["CIB_R11C11:CIB_PIC_B0"]), ["R11C12_HPBX0100", "R11C12_HPBX0500"]),

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
