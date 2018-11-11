from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

dsp_tiles = [
    "MIB_R13C60:MIB_DSP0", "MIB_R13C60:MIB2_DSP0",
    "MIB_R13C61:MIB_DSP1", "MIB_R13C61:MIB2_DSP1",
    "MIB_R13C62:MIB_DSP2", "MIB_R13C62:MIB2_DSP2",
    "MIB_R13C63:MIB_DSP3", "MIB_R13C63:MIB2_DSP3",
    "MIB_R13C64:MIB_DSP4", "MIB_R13C64:MIB2_DSP4",
    "MIB_R13C65:MIB_DSP5", "MIB_R13C65:MIB2_DSP5",
    "MIB_R13C66:MIB_DSP6", "MIB_R13C66:MIB2_DSP6",
    "MIB_R13C67:MIB_DSP7", "MIB_R13C67:MIB2_DSP7",
    "MIB_R13C68:MIB_DSP8", "MIB_R13C68:MIB2_DSP8",
]


def get_tiles(first):
    #
    # Get the list of tiles, placing a certain tile first so it is prioritised for fixed conns
    return [first] + [_ for _ in dsp_tiles if _ != first]


jobs = [
    ((13, 60), FuzzConfig(job="DSPROUTE0", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C60:MIB_DSP0"))),
    ((13, 61), FuzzConfig(job="DSPROUTE1", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C61:MIB_DSP1"))),
    ((13, 62), FuzzConfig(job="DSPROUTE2", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C62:MIB_DSP2"))),
    ((13, 63), FuzzConfig(job="DSPROUTE3", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C63:MIB_DSP3"))),
    ((13, 64), FuzzConfig(job="DSPROUTE4", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C64:MIB_DSP4"))),
    ((13, 65), FuzzConfig(job="DSPROUTE5", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C65:MIB_DSP5"))),
    ((13, 66), FuzzConfig(job="DSPROUTE6", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C66:MIB_DSP6"))),
    ((13, 67), FuzzConfig(job="DSPROUTE7", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C67:MIB_DSP7"))),
    ((13, 68), FuzzConfig(job="DSPROUTE8", family="ECP5", device="LFE5U-25F", ncl="dsproute.ncl",
                          tiles=get_tiles("MIB_R13C68:MIB_DSP8")))
]


def main():
    pytrellis.load_database("../../../database")
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
