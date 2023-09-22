import re
import tiles
import json
lc_input_re = re.compile(r'(J?[ABCDM]|CLK|LSR|CE)\d')
lc_output_re = re.compile(r'J?[FQ]|CLK\d')

def get_span(wire):
    if (wire.startswith("H") or wire.startswith("V")) and wire[1:3].isdigit():
        return "span" + wire[2] + wire[0].lower() + wire[3].lower()
    return None


def is_denorm(wire):
    if (wire.startswith("H06") or wire.startswith("V06")) and not wire.endswith("03"):
        return True
    if (wire.startswith("H02") or wire.startswith("V02")) and not wire.endswith("01"):
        return True
    return False


def get_distance(a, b):
    ra, ca = tiles.pos_from_name(a, (126, 95), 0, 0)
    rb, cb = tiles.pos_from_name(b, (126, 95), 0, 0)
    return abs(ra-rb) + abs(ca-cb)


def format_rel(a, b):
    ra, ca = tiles.pos_from_name(a, (126, 95), 0, 0)
    rb, cb = tiles.pos_from_name(b, (126, 95), 0, 0)
    rel = ""
    if rb < ra:
        rel += "n{}".format(ra-rb)
    elif rb > ra:
        rel += "s{}".format(rb-ra)

    if cb < ca:
        rel += "w{}".format(ca-cb)
    elif cb > ca:
        rel += "e{}".format(cb-ca)

    if rel != "":
        rel = "_" + rel
    return rel


def get_pip_class(source, sink):
    source_loc, source_base = source.split("_", 1)
    sink_loc, sink_base = sink.split("_", 1)
    if is_denorm(source_base) or is_denorm(sink_base):
        return None
    if source_base.endswith("_SLICE") or source_base.startswith("MUX") or sink_base.endswith("_SLICE"):
        return "slice_internal"
    if sink_base.endswith("_EBR") or source_base.endswith("_EBR"):
        return "ebr_internal"
    if "TEST" in sink_base or "TEST" in source_base:
        return None
    if "ALU" in sink_base or "ALU" in source_base or "MULT" in sink_base or "MULT" in source_base or "PRADD" in sink_base:
        return "dsp_internal"
    if lc_input_re.match(sink_base):
        if lc_output_re.match(source_base):
            return "{}_to_{}".format(source_base[:-1].lower(), sink_base[:-1].lower())
        elif get_span(source_base) is not None:
            return get_span(source_base)  + "_to_" + sink_base[:-1].lower() + format_rel(source_loc, sink_loc)
        elif "HPBX" in source_base:
            return "global_to_" + sink_base[:-1].lower()
        else:
            return None
    elif get_span(sink_base) is not None:
        if lc_output_re.match(source_base):
            return source_base[:-1].lower() + "_to_" + get_span(sink_base) + format_rel(source_loc, sink_loc)
        elif get_span(source_base) is not None:
            return  get_span(source_base) + "_to_" + get_span(sink_base) + format_rel(source_loc, sink_loc)
        elif "HPBX" in source_base:
            return "global_to_" + get_span(sink_base)
        elif "BOUNCE" in source_base:
            return None
        elif "KEEP" in source_base:
            return None
        else:
            assert False, (source, sink)
    elif source_base.startswith("LSR") and sink_base.startswith("MUXLSR"):
        return "lsr_to_muxlsr"
    else:
        return None

# Force these pip classes to have a 0 fanout adder for a better solution
zero_fanout_classes = {
    "span0hr_to_ce",
    "span0vt_to_lsr",
    "span1he_to_m",
    "span1he_to_m_w1",
    "span1he_to_span2vn_n1",
    "span1he_to_span6he_e3",
    "span1hw_to_m",
    "span1hw_to_m_w1",
    "span1hw_to_span6hw_w4",
    "span1vn_to_span2vn_n1",
    "span1vn_to_span6he_e3",
    "span1vn_to_span6hw_w3",
    "span2he_to_lsr",
    "span2he_to_lsr_e1",
    "span2he_to_m",
    "span2he_to_span2vn_n1",
    "span2he_to_span2vn_n1e1",
    "span2he_to_span6he_e4",
    "span2hw_to_lsr",
    "span2hw_to_lsr_w1",
    "span2hw_to_m",
    "span2hw_to_m_w1",
    "span2hw_to_span2vn_n1",
    "span2hw_to_span2vn_n1w1",
    "span2hw_to_span6hw_w4",
    "span6vs_to_span1vs_s3",
    "span6vn_to_span6he_e3",
    "span6vn_to_span6he_n3e3",
    "span6vn_to_span6hw_w3",
    "span6vs_to_span2vn_s2",
    "span6vs_to_span6he_e3",
    "span6vs_to_span6hw_s3w3",
    "span1he_to_span1hw",
    "span1vn_to_m_s1",
    "span1vs_to_m",
    "span6he_to_span1he_e3",
    "span2vs_to_c",
    "span0hr_to_m",
}


def force_zero_fanout_pip(name):
    return name.startswith("jf") or name.startswith("jq") or "to_j" in name or name.startswith("q_to_") or name == "slice_internal" or name == "ebr_internal" or name in zero_fanout_classes

# Force these pip classes to have zero delay to avoid linear dependence and unstable results

zero_delay_classes = {
    "ebr_internal",
    "f_to_span1he_e1",
    "f_to_span1hw",
    "f_to_span1vs",
    "f_to_span2vn_n1",
    "f_to_span6hw_w3",
    "jf_to_span1he_e1",
    "jf_to_span1hw",
    "jf_to_span2vn_n1",
    "jq_to_span1hw",
    "jq_to_span6hw_w3",
    "lsr_to_muxlsr",
    "q_to_span1hw",
    "q_to_span1vs",
    "q_to_span2vn_n1",
    "q_to_span6he_e3",
    "q_to_span6hw_w3",
    "span0hl_to_c"
    "span0hl_to_ce",
    "span0hl_to_d",
    "span0hl_to_m",
    "span0vt_to_lsr",
    "span1he_to_span2vn_n1",
    "span1he_to_span6he_e3",
    "span1hw_to_span6hw_w4",
    "span1vn_to_span2vn_n1",
    "span1vn_to_span6he_e3",
    "span1vn_to_span6hw_w3",
    "span2he_to_lsr",
    "span2he_to_lsr_e1",
    "span2he_to_span2vn_n1",
    "span2he_to_span2vn_n1e1",
    "span2he_to_span6he_e4",
    "span2hw_to_lsr",
    "span2hw_to_lsr_w1",
    "span2hw_to_span2vn_n1",
    "span2hw_to_span2vn_n1w1",
    "span2hw_to_span6hw_w4",
    "span2vs_to_d",
    "span2vs_to_span0hr",
    "span2vs_to_span0vb",
    "span6vn_to_span1vs_n3",
    "span6vs_to_span1vs_s3",
    "span6vs_to_span2vn_s2",
    "span6vs_to_span6hw_w3",
    "span6vn_to_span6he_e3",
    "span6vn_to_span6he_n3e3",
    "span6vn_to_span6hw_w3",
    "span6vs_to_span2vn_s2",
    "span6vs_to_span6he_e3",
    "span6vs_to_span6hw_s3w3",
    "span1he_to_span1hw",
    "span6he_to_span1he_e3",

}

def force_zero_delay_pip(name):
    return name in zero_delay_classes