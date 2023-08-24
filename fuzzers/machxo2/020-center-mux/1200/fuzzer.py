from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re
import argparse
from mk_nets import *

def fc_filter_all(a, n):
    return True

# TCL claims these are fixed connections; we should treat them as
# inputs/outputs to/from DCC/DCM BELs.
def fc_filter_dcc(a, n):
    return bool(not (nets.machxo2.dcc_sig_re.match(a[0]) and nets.machxo2.dcc_sig_re.match(a[1])) and
                not (nets.machxo2.dcm_sig_re.match(a[0]) and nets.machxo2.dcm_sig_re.match(a[1])))

# The relevant tiles were inferred from the center_mux experiment.
# Asterisk means "the fuzzer generated connects with non-local prefixes".
jobs = [
        # *
        {
            "netnames" : eclk_out + eclk_cib + eclk_div,
            "cfg" : FuzzConfig(job="GLOBAL_ECLK", family="MachXO2", device="LCMXO2-1200HC", ncl="center-mux.ncl",
                      tiles=["CENTER6:CENTER_EBR_CIB", "CENTER_EBR14:CENTER_EBR",
                             "CENTER9:CENTER8", "CENTER8:CENTER7", "CENTER7:CENTER6",
                             "CENTER5:CENTER5", "CENTER4:CENTER4"]),
            "prefix" : "1200_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_all
        },

        # *
        {
            "netnames" : eclkbridge,
            "cfg" : FuzzConfig(job="GLOBAL_ECLKBRIDGE", family="MachXO2", device="LCMXO2-1200HC", ncl="center-mux.ncl",
                      tiles=["CENTER6:CENTER_EBR_CIB", "CENTER_EBR14:CENTER_EBR",
                             "CENTER9:CENTER8", "CENTER8:CENTER7", "CENTER7:CENTER6",
                             "CENTER5:CENTER5", "CENTER4:CENTER4"]),
            "prefix" : "1200_",
            "overrides" : { "R6C13_JECSOUT0_ECLKBRIDGECS" : "driver",
                            "R6C13_JECSOUT1_ECLKBRIDGECS" : "driver",
                            "R6C13_JSEL0_ECLKBRIDGECS" : "sink",
                            "R6C13_JSEL1_ECLKBRIDGECS" : "sink" },
            "fc_filter" : fc_filter_all
        },

        {
            "netnames" : dcm + dcc,
            "cfg" : FuzzConfig(job="GLOBAL_DCM_DCC", family="MachXO2", device="LCMXO2-1200HC", ncl="center-mux.ncl",
                      tiles=["CENTER6:CENTER_EBR_CIB", "CENTER_EBR14:CENTER_EBR",
                             "CENTER9:CENTER8", "CENTER8:CENTER7", "CENTER7:CENTER6",
                             "CENTER5:CENTER5", "CENTER4:CENTER4"]),
            "prefix" : "1200_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_dcc
        },

        {
            "netnames" : hfsn_cib + hfsn_out + global_cib + global_out + pll + clock_pin,
            "cfg" : FuzzConfig(job="GLOBAL_HFSN", family="MachXO2", device="LCMXO2-1200HC", ncl="center-mux.ncl",
                      tiles=["CENTER6:CENTER_EBR_CIB", "CENTER_EBR14:CENTER_EBR",
                             "CENTER9:CENTER8", "CENTER8:CENTER7", "CENTER7:CENTER6",
                             "CENTER5:CENTER5", "CENTER4:CENTER4"]),
            "prefix" : "1200_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_all
        },

        # Thanks to fc_filter_dcc, make sure to manually connect DCC outputs to
        # entrance to global network!
        {
            "netnames" : ["R6C13_VPRX0000", "R6C13_VPRX0100", "R6C13_VPRX0200", "R6C13_VPRX0300",
                          "R6C13_VPRX0400", "R6C13_VPRX0500", "R6C13_VPRX0600", "R6C13_VPRX0700"],
            "cfg" : FuzzConfig(job="GLOBAL_DCC_OUT", family="MachXO2", device="LCMXO2-1200HC", ncl="center-mux.ncl",
                      tiles=["CENTER6:CENTER_EBR_CIB", "CENTER_EBR14:CENTER_EBR",
                             "CENTER9:CENTER8", "CENTER8:CENTER7", "CENTER7:CENTER6",
                             "CENTER5:CENTER5", "CENTER4:CENTER4"]),
            "prefix" : "1200_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_all
        },
]


def main(args):
    pytrellis.load_database("../../../../database")

    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        cfg.setup()
        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=job["netnames"],
                                                     netname_filter_union=False,
                                                     netdir_override=job["overrides"],
                                                     nonlocal_prefix=job["prefix"],
                                                     fc_predicate=job["fc_filter"])

    # TODO: R6C13_JA0 --> R6C13_JCE0_DCC. But TCL also claims
    # R6C13_CLKI0_DCC --> R6C13_CLKO0_DCC (pseudo = 1). Contradiction?
    # From talking to Dave: No it's not a contradiction. A
    # config bit controls whether JCE0 has any effect.
    # Might be fuzzed with something like:
    # interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=["R6C13_CLKI0_DCC", "R6C13_CLKO0_DCC", "R6C13_JCE0_DCC"],
    #                                              netname_filter_union=False,
    #                                              netdir_override = {
    #                                                 "R6C13_JCE0_DCC" : "sink",
    #                                              })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Center Mux Routing Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
