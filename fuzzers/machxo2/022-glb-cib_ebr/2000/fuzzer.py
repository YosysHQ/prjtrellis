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
        net_product(["R5C{}_VPTX0{{}}00", "R11C{}_VPTX0{{}}00"], [tilepos[1]]),
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
    (FuzzConfig(job="CIB0_EBR0_END0_UPDOWN", family="MachXO2", device="LCMXO2-2000HC", ncl="tap.ncl",
                      tiles=["CIB_R8C1:CIB_EBR_DUMMY_END3"]), flatten_nets((8,1))),
    (FuzzConfig(job="CIB0_EBR2_END1_UPDOWN", family="MachXO2", device="LCMXO2-2000HC", ncl="tap.ncl",
                      tiles=["CIB_R8C26:CIB_EBR2_END0"]), flatten_nets((8,26)))
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
