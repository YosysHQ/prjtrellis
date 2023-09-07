from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re
import argparse

jobs = [
        {
            "cfg": FuzzConfig(job="CIBEBR0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute_1200.ncl", tiles=["CIB_R6C10:CIB_EBR0"]),
            "location": (6, 10),
            "nn_filter_extra": []
        },
        {
            "cfg": FuzzConfig(job="CIBEBR0END0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute_1200.ncl", tiles=["CIB_R6C1:CIB_EBR0_END0"]),
            "location": (6, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },
        {
            "cfg": FuzzConfig(job="CIBEBR2END0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute_1200.ncl", tiles=["CIB_R6C22:CIB_EBR2_END0"]),
            "location": (6, 22),
            "nn_filter_extra": []
        },
        # CIB_EBR0_END2_DLL3 and CIB_EBR0_END2_DLL45 identical
        {
            "cfg": FuzzConfig(job="CIB_EBR0_END2_DLL3ROUTE", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="cibroute_7000.ncl", tiles=["CIB_R20C1:CIB_EBR0_END2_DLL3"]),
            "location": (20, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR0_END2_DLL45ROUTE", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="cibroute_7000.ncl", tiles=["CIB_R13C1:CIB_EBR0_END2_DLL45"]),
            "location": (13, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },

        {
            "cfg": FuzzConfig(job="CIB_EBR2_END1ROUTE", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="cibroute_7000.ncl", tiles=["CIB_R13C41:CIB_EBR2_END1"]),
            "location": (13, 41),
            "nn_filter_extra": []
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR2_END1_SPROUTE", family="MachXO2", device="LCMXO2-7000HC",
                        ncl="cibroute_7000.ncl", tiles=["CIB_R20C41:CIB_EBR2_END1_SP"]),
            "location": (20, 41),
            "nn_filter_extra": []
        },

        {
            "cfg": FuzzConfig(job="CIB_EBR0_END1ROUTE", family="MachXO2", device="LCMXO2-4000HC",
                        ncl="cibroute_4000.ncl", tiles=["CIB_R11C1:CIB_EBR0_END1"]),
            "location": (11, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },

        {
            "cfg": FuzzConfig(job="CIB_EBR_DUMMY_END3ROUTE", family="MachXO2", device="LCMXO2-2000HC",
                        ncl="cibroute_2000.ncl", tiles=["CIB_R8C1:CIB_EBR_DUMMY_END3"]),
            "location": (8, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },
]


def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        cfg.setup()

        span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')

        def nn_filter(net, netnames):
            """I want to handle global nets that are associated with this
            tile manually; any matching nets are filtered out."""
            if net in job["nn_filter_extra"]:
                return False

            """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
            left out by Tcl"""
            return ((net in netnames or span1_re.match(net)) and nets.is_cib(net)) or nets.machxo2.is_global(net)

        def fc_filter(arc, netnames):
            """ Ignore connections between two general routing nets. These are edge buffers which vary based on location
            and must be excluded from the CIB database.
            """
            return not (nets.general_routing_re.match(arc[0]) and nets.general_routing_re.match(arc[1]))
        interconnect.fuzz_interconnect(config=cfg, location=job["location"],
                                       netname_predicate=nn_filter,
                                       fc_predicate=fc_filter,
                                       netname_filter_union=True,
                                       enable_span1_fix=True,
                                       netdir_override=defaultdict(lambda : str("ignore")))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIB_EBRn Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
