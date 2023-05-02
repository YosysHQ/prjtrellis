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
            "cfg" : FuzzConfig(job="GLOBAL_ECLK", family="MachXO3", device="LCMXO3LF-6900C", ncl="center-mux.ncl",
                      tiles=["CENTER13:CENTER_EBR_CIB_4K", "CENTER_EBR29:CENTER_EBR",
                             "CENTER16:CENTER8", "CENTER15:CENTER7", "CENTER14:CENTER6",
                             "CENTER11:CENTERB", "CENTER12:CENTERC"]),
            "prefix" : "6900_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_all
        },

        # *
        {
            "netnames" : eclkbridge,
            "cfg" : FuzzConfig(job="GLOBAL_ECLKBRIDGE", family="MachXO3", device="LCMXO3LF-6900C", ncl="center-mux.ncl",
                      tiles=["CENTER13:CENTER_EBR_CIB_4K", "CENTER_EBR29:CENTER_EBR",
                             "CENTER16:CENTER8", "CENTER15:CENTER7", "CENTER14:CENTER6",
                             "CENTER11:CENTERB", "CENTER12:CENTERC"]),
            "prefix" : "6900_",
            "overrides" : { "R13C19_JECSOUT0_ECLKBRIDGECS" : "driver",
                            "R13C19_JECSOUT1_ECLKBRIDGECS" : "driver",
                            "R13C19_JSEL0_ECLKBRIDGECS" : "sink",
                            "R13C19_JSEL1_ECLKBRIDGECS" : "sink" },
            "fc_filter" : fc_filter_all
        },

        {
            "netnames" : dcm + dcc,
            "cfg" : FuzzConfig(job="GLOBAL_DCM_DCC", family="MachXO3", device="LCMXO3LF-6900C", ncl="center-mux.ncl",
                      tiles=["CENTER13:CENTER_EBR_CIB_4K", "CENTER_EBR29:CENTER_EBR",
                             "CENTER16:CENTER8", "CENTER15:CENTER7", "CENTER14:CENTER6",
                             "CENTER11:CENTERB", "CENTER12:CENTERC"]),
            "prefix" : "6900_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_dcc
        },

        {
            "netnames" : hfsn_cib + hfsn_out + global_cib + global_out + pll + clock_pin,
            "cfg" : FuzzConfig(job="GLOBAL_HFSN", family="MachXO3", device="LCMXO3LF-6900C", ncl="center-mux.ncl",
                      tiles=["CENTER13:CENTER_EBR_CIB_4K", "CENTER_EBR29:CENTER_EBR",
                             "CENTER16:CENTER8", "CENTER15:CENTER7", "CENTER14:CENTER6",
                             "CENTER11:CENTERB", "CENTER12:CENTERC"]),
            "prefix" : "6900_",
            "overrides" : defaultdict(lambda : str("sink")),
            "fc_filter" : fc_filter_all
        },

        # Thanks to fc_filter_dcc, make sure to manually connect DCC outputs to
        # entrance to global network!
        {
            "netnames" : ["R13C19_VPRX0000", "R13C19_VPRX0100", "R13C19_VPRX0200", "R13C19_VPRX0300",
                          "R13C19_VPRX0400", "R13C19_VPRX0500", "R13C19_VPRX0600", "R13C19_VPRX0700"],
            "cfg" : FuzzConfig(job="GLOBAL_DCC_OUT", family="MachXO3", device="LCMXO3LF-6900C", ncl="center-mux.ncl",
                      tiles=["CENTER13:CENTER_EBR_CIB_4K", "CENTER_EBR29:CENTER_EBR",
                             "CENTER16:CENTER8", "CENTER15:CENTER7", "CENTER14:CENTER6",
                             "CENTER11:CENTERB", "CENTER12:CENTERC"]),
            "prefix" : "6900_",
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

    # TODO: R13C19_JA0 --> R13C19_JCE0_DCC. But TCL also claims
    # R13C19_CLKI0_DCC --> R13C19_CLKO0_DCC (pseudo = 1). Contradiction?
    # From talking to Dave: No it's not a contradiction. A
    # config bit controls whether JCE0 has any effect.
    # Might be fuzzed with something like:
    # interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=["R13C19_CLKI0_DCC", "R13C19_CLKO0_DCC", "R13C19_JCE0_DCC"],
    #                                              netname_filter_union=False,
    #                                              netdir_override = {
    #                                                 "R13C19_JCE0_DCC" : "sink",
    #                                              })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Center Mux Routing Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
