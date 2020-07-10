from fuzzconfig import FuzzConfig
import interconnect
import pytrellis
from nets import net_product

def mk_nets(tilepos, glb_ids):
    ud_nets = []
    rc_prefix = "R{}C{}_".format(tilepos[0], tilepos[1])

    # Up/Down conns
    ud_nets.extend(net_product(
        net_product(["R4C{}_VPTX0{{}}00", "R9C{}_VPTX0{{}}00"], [tilepos[1]]),
        glb_ids))

    # Phantom DCCs- First fill in "T"/"B", and then global id
    ud_nets.extend(net_product(
        net_product([rc_prefix + "CLKI{{}}{}_DCC",
                     # rc_prefix + "JCE{{}}{}_DCC", # TODO: These nets may not exist?
                     rc_prefix + "CLKO{{}}{}_DCC"], ("T", "B")),
        glb_ids))

    return ud_nets

jobs = [
    (FuzzConfig(job="GLB_UPDOWN26", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C4:CIB_EBR0"]), mk_nets((6, 4), (2, 6))),
    (FuzzConfig(job="GLB_UPDOWN15", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C7:CIB_EBR0"]), mk_nets((6, 7), (1, 5))),
    (FuzzConfig(job="GLB_UPDOWN04", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C10:CIB_EBR0"]), mk_nets((6, 10), (0, 4))),
    (FuzzConfig(job="GLB_UPDOWN37", family="MachXO2", device="LCMXO2-1200HC", ncl="tap.ncl",
                      tiles=["CIB_R6C17:CIB_EBR0"]), mk_nets((6, 17), (3, 7))),
]

def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg, netnames = job
        cfg.setup()
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False)


if __name__ == "__main__":
    main()
