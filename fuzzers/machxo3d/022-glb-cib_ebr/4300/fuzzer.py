from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
import argparse
from nets import net_product

def mk_nets(tilepos, glb_ids):
    ud_nets = []
    rc_prefix = "R{}C{}_".format(tilepos[0], tilepos[1])

    # Up/Down conns
    ud_nets.extend(net_product(
        net_product(["R6C{}_VPTX0{{}}00", "R16C{}_VPTX0{{}}00"], [tilepos[1]]),
        glb_ids))

    # Phantom DCCs- First fill in "T"/"B", and then global id
    ud_nets.extend(net_product(
        net_product([rc_prefix + "CLKI{{}}{}_DCC",
                     # rc_prefix + "JCE{{}}{}_DCC", # TODO: These nets may not exist?
                     rc_prefix + "CLKO{{}}{}_DCC"], ("T", "B")),
        glb_ids))

    return ud_nets

def flatten_nets(tilepos):
    return [nets for netpair in [(0, 4), (1, 5), (2, 6), (3, 7)] for nets in mk_nets(tilepos, netpair)]

jobs = [
    (FuzzConfig(job="GLB_UPDOWN26", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap.ncl",
                      tiles=["CIB_R11C4:CIB_EBR0"]), mk_nets((11, 4), (3, 7))),
    (FuzzConfig(job="GLB_UPDOWN15", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap.ncl",
                      tiles=["CIB_R11C7:CIB_EBR0"]), mk_nets((11, 7), (2, 6))),
    (FuzzConfig(job="GLB_UPDOWN04", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap.ncl",
                      tiles=["CIB_R11C10:CIB_EBR0"]), mk_nets((11, 10), (1, 5))),
    (FuzzConfig(job="GLB_UPDOWN37", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap.ncl",
                      tiles=["CIB_R11C13:CIB_EBR0"]), mk_nets((11, 13), (0, 4))),

    (FuzzConfig(job="CIB_EBR0_END1_UPDOWN", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap.ncl",
                      tiles=["CIB_R11C1:CIB_EBR0_END1"]), flatten_nets((11,1))),
    (FuzzConfig(job="CIB_EBR2_END1_UPDOWN", family="MachXO3D", device="LCMXO3D-4300HC", ncl="tap.ncl",
                      tiles=["R11C33:CIB_EBR2_END1"]), flatten_nets((11,32))),

]

def main(args):
    pytrellis.load_database("../../../../database")

    for job in [jobs[i] for i in args.ids]:
        cfg, netnames = job
        cfg.setup()
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     bidir=True,
                                                     netname_filter_union=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Center Mux Routing Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
