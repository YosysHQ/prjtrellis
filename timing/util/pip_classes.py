import re
import tiles
lc_input_re = re.compile(r'[ABCDM]\d')
lc_output_re = re.compile(r'[FQ]\d')

def get_span(wire):
    if (wire.startswith("H") or wire.startswith("V")) and wire[1:3].isdigit():
        return "span" + wire[2]  + wire[0].lower()
    return None


def is_denorm(wire):
    if (wire.startswith("H06") or wire.startswith("V06")) and not wire.endswith("03"):
        return True
    if (wire.startswith("H02") or wire.startswith("V02")) and not wire.endswith("01"):
        return True
    return False


def get_distance(a, b):
    ra, ca = tiles.pos_from_name(a)
    rb, cb = tiles.pos_from_name(b)
    return abs(ra-rb) + abs(ca-cb)


def get_pip_class(source, sink):
    source_loc, source_base = source.split("_", 1)
    sink_loc, sink_base = sink.split("_", 1)
    if is_denorm(source_base) or is_denorm(sink_base):
        return None
    if source_base.endswith("_SLICE") or source_base.startswith("MUX") or sink_base.endswith("_SLICE"):
        return "slice_internal"
    if lc_input_re.match(sink_base):
        if lc_output_re.match(source_base):
            return "slice_out_to_slice_in"
        elif get_span(source_base) is not None:
            return get_span(source_base)  + "_to_slice_in_dist_" + str(get_distance(source_loc, sink_loc))
        else:
            assert False, (source, sink)
    elif get_span(sink_base) is not None:
        if lc_output_re.match(source_base):
            return  "slice_out_to_" + get_span(sink_base) + "_dist" + str(get_distance(source_loc, sink_loc))
        elif get_span(source_base) is not None:
            return  get_span(source_base) + "_to_" + get_span(sink_base) + "_dist" + str(get_distance(source_loc, sink_loc))
        elif source_base.startswith("HPBX"):
            return "global_to_" + get_span(sink_base)
        else:
            assert False, (source, sink)
    else:
        return None


def force_zero_pip(name):
    return name == "slice_internal"