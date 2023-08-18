from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re
import argparse

jobs = [
        #0
        {
            "cfg": FuzzConfig(job="CIBEBR0ROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R8C10:CIB_EBR0"]),
            "location": (8, 10),
            "nn_filter_extra": []
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR0_10KROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R15C22:CIB_EBR0_10K"]),
            "location": (15, 22),
            "nn_filter_extra": []
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR0_END0_10KROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R15C1:CIB_EBR0_END0_10K"]),
            "location": (15, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR2_END1_10KROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R15C49:CIB_EBR2_END1_10K"]),
            "location": (15, 49),
            "nn_filter_extra": []
        },
        #4
        {
            "cfg": FuzzConfig(job="CIB_EBR0_END0_DLL3ROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R22C1:CIB_EBR0_END0_DLL3"]),
            "location": (22, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR0_END0_DLL5ROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R8C1:CIB_EBR0_END0_DLL5"]),
            "location": (8, 1),
            "nn_filter_extra": ["G_HPBX0100", "G_HPBX0500"]
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR2_END1ROUTE", family="MachXO3D", device="LCMXO3D-4300HC",
                        ncl="cibroute_4300.ncl", tiles=["R11C33:CIB_EBR2_END1"]),
            "location": (11, 32),
            "nn_filter_extra": []
        },
        {
            "cfg": FuzzConfig(job="CIB_EBR2_END1_SPROUTE", family="MachXO3D", device="LCMXO3D-9400HC",
                        ncl="cibroute_9400.ncl", tiles=["CIB_R8C49:CIB_EBR2_END1_SP"]),
            "location": (8, 49),
            "nn_filter_extra": []
        },
        #8
        {
            "cfg": FuzzConfig(job="CIB_EBR0_END1ROUTE", family="MachXO3D", device="LCMXO3D-4300HC",
                        ncl="cibroute_4300.ncl", tiles=["CIB_R11C1:CIB_EBR0_END1"]),
            "location": (11, 1),
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
