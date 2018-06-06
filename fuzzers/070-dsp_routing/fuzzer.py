from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

dsp_tiles = [
    "MIB_R13C13:MIB_DSP0", "MIB_R13C13:MIB2_DSP0",
    "MIB_R13C14:MIB_DSP1", "MIB_R13C14:MIB2_DSP1",
    "MIB_R13C15:MIB_DSP2", "MIB_R13C15:MIB2_DSP2",
    "MIB_R13C16:MIB_DSP3", "MIB_R13C16:MIB2_DSP3",
    "MIB_R13C17:MIB_DSP4", "MIB_R13C17:MIB2_DSP4",
    "MIB_R13C18:MIB_DSP5", "MIB_R13C18:MIB2_DSP5",
    "MIB_R13C19:MIB_DSP6", "MIB_R13C19:MIB2_DSP6",
    "MIB_R13C20:MIB_DSP7", "MIB_R13C20:MIB2_DSP7",
    "MIB_R13C21:MIB_DSP8", "MIB_R13C21:MIB2_DSP8",
]


def get_tiles(first):
    #
    # Get the list of tiles, placing a certain tile first so it is prioritised for fixed conns
    return [first] + [_ for _ in dsp_tiles if _ != first]


jobs = [
    ((13, 13), FuzzConfig(job="DSPROUTE0", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C13:MIB_DSP0"))),
    ((13, 14), FuzzConfig(job="DSPROUTE1", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C14:MIB_DSP1"))),
    ((13, 15), FuzzConfig(job="DSPROUTE1", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C15:MIB_DSP2"))),
]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        loc, cfg = job
        cfg.setup()

        def nn_filter(net, netnames):
            return ("MULT" in net) or ("ADD" in net) or ("JMUI" in net) or ("JP" in net) \
                   or ("DSP" in net) or ("JSRO" in net) or ("JNEXTR" in net) \
                   or ("JCFB" in net) or ("JPSR"in net) or ("JMSR" in net) or ("JR" in net) \
                   or ("ALU" in net) or ("JCO" in net) or ("JSOURCE" in net)
        interconnect.fuzz_interconnect(config=cfg, location=loc,
                                       netname_predicate=nn_filter,
                                       netname_filter_union=False,
                                       func_cib=True)


if __name__ == "__main__":
    main()
