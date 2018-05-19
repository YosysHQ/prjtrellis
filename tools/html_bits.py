#!/usr/bin/env python3

"""Generate a HTML representation of the tile bit database"""

import pytrellis
import argparse
import sys


def find_bits(db):
    cwords = db.get_settings_words()
    for cword in cwords:
        wd = db.get_data_for_setword(cword)
        for bits in wd.bits:
            for bit in bits.bits:
                bitmap[bit.frame, bit.bit] = "word_" + str(cword)
    cenums = db.get_settings_enums()
    for cenum in cenums:
        ed = db.get_data_for_enum(cenum)
        for opt in ed.get_options():
            for bit in ed.options[opt].bits:
                bitmap[bit.frame, bit.bit] = "enum_" + str(cenum)
    sinks = db.get_sinks()
    for sink in sinks:
        mux = db.get_mux_data_for_sink(sink)
        for arc in mux.arcs:
            for bit in arc.bits.bits:
                bitmap[bit.frame, bit.bit] = "mux_" + str(sink)


def mux_html(mux, f):
    bitset = set()
    for arc in mux.arcs:
        for bit in arc.bits.bits:
            bitset.add((bit.frame, bit.bit))

    bitlist = list(sorted(bitset))
    print('<h3 id="mux_{}">Mux driving <span class="mux_sink">{}</span></h3>'.format(mux.sink, mux.sink), file=f)
    print('<table class="mux"><tr><th>Source</th>', file=f)
    for bit in bitlist:
        print('<th style="padding-left: 10px; padding-right: 10px">F{}B{}</th>'.format(bit[0], bit[1]), file=f)
    print('</tr>', file=f)
    truthtable = []
    for arc in mux.arcs:
        ttrow = []
        for blb in bitlist:
            found = False
            for ab in arc.bits.bits:
                if ab.frame == blb[0] and ab.bit == blb[1]:
                    ttrow.append('0' if ab.inv else '1')
                    found = True
                    break
            if not found:
                ttrow.append("-")
        truthtable.append((arc, ttrow))
    trstyle = ""
    for (arc, ttrow) in sorted(truthtable, key=lambda x: "".join(reversed(x[1])).replace("-", "0")):
        trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
        print('<tr {}><td>{}</td>'.format(trstyle, arc.source), file=f)
        for bit in ttrow:
            print('<td style="text-align: center">{}</td>'.format(bit), file=f)
        print('</td>', file=f)

    print('</table>', file=f)


def setword_html(word, f):
    print('<h3 id="word_{}">Configuration {} {}</h3>'.format(word.name, "bit" if len(word.bits) == 1 else "word",
                                                             word.name), file=f)
    print('<p>Default value: {}\'b{}</p>'.format(len(word.defval),
                                                 "".join(reversed(["1" if _ else "0" for _ in word.defval]))), file=f)
    print('<table class="setword">', file=f)
    trstyle = ""
    for idx in range(len(word.bits)):
        cbits = " ".join(["{}F{}B{}".format("!" if b.inv else "", b.frame, b.bit) for b in word.bits[idx].bits])
        trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
        print(
            '<tr {}><td style="padding-left: 10px; padding-right: 10px">{}[{}]</td><td style="padding-left: 10px; padding-right: 10px">{}</td></tr>'.format(
                trstyle, word.name, idx, cbits), file=f)
    print('</table>', file=f)


def muxes_html(db, f):
    sinks = db.get_sinks()
    for sink in sorted(sinks):
        mux = db.get_mux_data_for_sink(sink)
        mux_html(mux, f)


def setwords_html(db, f):
    words = db.get_settings_words()
    for name in sorted(words):
        word = db.get_data_for_setword(name)
        setword_html(word, f)

def fixed_conns_html(db, f):
    print("<h3>Fixed Connections</h3>", file=f)
    print('<table class="fconn"><tr><th>Source</th><th>Sink</th></tr>', file=f)
    conns = db.get_fixed_conns()
    trstyle = ""
    for conn in conns:
        trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
        print(
            '<tr {}><td style="padding-left: 10px; padding-right: 10px">{}</td><td style="padding-left: 10px; padding-right: 10px">{}</td></tr>'.format(
                trstyle, conn.source, conn.sink), file=f)
    print('</table>', file=f)


def get_bit_info(frame, bit):
    if (frame, bit) in bitmap:
        group = bitmap[(frame, bit)]
        if group.startswith("mux"):
            label = group.split("_")[-1][0]
            colour = "#FF8888"
        elif group.startswith("enum") or group.startswith("word"):
            label = "C"
            colour = "#88FF88"
        else:
            label = "?"
            colour = "#ffffff"
        return group, label, colour
    else:
        return "unknown", "&nbsp;", "#FFFFFF"


def bit_grid_html(tileinfo, f):
    print("<table style='font-size: 8pt; border: 2px solid black; text-align: center'>", file=f)
    for bit in range(tileinfo.bits_per_frame):
        print("<tr style='height: 20px'>", file=f)
        for frame in range(tileinfo.num_frames):
            group, label, colour = get_bit_info(frame, bit)
            print("<td style='height: 100%; border: 2px solid black;'>", file=f)
            print("""<a href='#{}' title='F{}B{}' style='text-decoration: none; color: #000000'>
                    <div id='f{}b{}' style='height: 100%; background-color: {}; width: 12px' class='grp_{}'
                    onmouseover='mov(event);' onmouseout='mou(event);'>{}</div></a></td>""".format(
                group, frame, bit, frame, bit, colour, group, label), file=f)
        print("</tr>", file=f)
    print("</table>", file=f)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('family', type=str,
                    help="FPGA family (e.g. ECP5)")
parser.add_argument('device', type=str,
                    help="FPGA device (e.g. LFE5U-85F)")
parser.add_argument('tile', type=str,
                    help="Tile type (e.g. PLC2)")
parser.add_argument('outfile', type=argparse.FileType('w'),
                    help="output HTML file")


def main(argv):
    global bitmap
    bitmap = dict(dict())

    args = parser.parse_args(argv[1:])
    f = args.outfile
    print(
        """<html>
            <head><title>{} Bit Data</title>
        """.format(args.tile), file=f)
    print("""
            <script type="text/javascript">
            origClr = {};
            origClass = "";
            
            function mov(event) {
                if (event.target.className != "unknown") {
                    origClass = event.target.className;
                    var elems = document.getElementsByClassName(origClass);
                    for(var i = 0; i < elems.length; i++) {
                       if(!(elems[i].id in origClr)) {
                          origClr[elems[i].id] = elems[i].style.backgroundColor;
                       }
                       elems[i].style.backgroundColor = "white";
                    }

                }
            }
            
            function mou(event) {
                var elems = document.getElementsByClassName(origClass);
                for(var i = 0; i < elems.length; i++) {
                   elems[i].style.backgroundColor = origClr[elems[i].id] || "#ffffff";
                }
            }
            </script>
            </head>
            <body>
        """, file=f)
    print("""<h1>{} Bit Data</h1>
    """.format(args.tile), file=f)
    pytrellis.load_database("../database")
    tdb = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(args.family, args.device, args.tile))
    ch = pytrellis.Chip(args.device)
    ti = ch.get_tiles_by_type(args.tile)[0].info
    find_bits(tdb)
    bit_grid_html(ti, f)
    muxes_html(tdb, f)
    setwords_html(tdb, f)
    # TODO: enums
    fixed_conns_html(tdb, f)
    print("""</body></html>""", file=f)


if __name__ == "__main__":
    main(sys.argv)
