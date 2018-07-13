#!/usr/bin/env python3

"""Generate a HTML representation of the tile bit database"""

import pytrellis
import database
import argparse
import sys
import re


def find_bits(db):
    cwords = db.get_settings_words()
    for cword in cwords:
        wd = db.get_data_for_setword(cword)
        for i in range(len(wd.bits)):
            for bit in wd.bits[i].bits:
                bitmap[bit.frame, bit.bit] = "word_" + str(cword)
                if (bit.frame, bit.bit) not in labels:
                    labels[bit.frame, bit.bit] = set()
                labels[bit.frame, bit.bit].add("{}[{}]".format(cword, i))
    cenums = db.get_settings_enums()
    for cenum in cenums:
        ed = db.get_data_for_enum(cenum)
        for opt in ed.get_options():
            for bit in ed.options[opt].bits:
                bitmap[bit.frame, bit.bit] = "enum_" + str(cenum)
                if (bit.frame, bit.bit) not in labels:
                    labels[bit.frame, bit.bit] = set()
                labels[bit.frame, bit.bit].add(cenum)
    sinks = db.get_sinks()
    for sink in sinks:
        mux = db.get_mux_data_for_sink(sink)
        for src in mux.get_sources():
            for bit in mux.arcs[src].bits.bits:
                bitmap[bit.frame, bit.bit] = "mux_" + str(sink)
                if (bit.frame, bit.bit) not in labels:
                    labels[bit.frame, bit.bit] = set()
                labels[bit.frame, bit.bit].add(sink)


def mux_html(mux, f):
    bitset = set()
    for src in mux.get_sources():
        for bit in mux.arcs[src].bits.bits:
            bitset.add((bit.frame, bit.bit))

    bitlist = list(sorted(bitset))
    print('<h3 id="mux_{}">Mux driving <span class="mux_sink">{}</span></h3>'.format(mux.sink, mux.sink), file=f)
    print('<table class="mux"><tr><th>Source</th>', file=f)
    for bit in bitlist:
        print('<th style="padding-left: 10px; padding-right: 10px">F{}B{}</th>'.format(bit[0], bit[1]), file=f)
    print('</tr>', file=f)
    truthtable = []
    for src in mux.get_sources():
        ttrow = []
        for blb in bitlist:
            found = False
            for ab in mux.arcs[src].bits.bits:
                if ab.frame == blb[0] and ab.bit == blb[1]:
                    ttrow.append('0' if ab.inv else '1')
                    found = True
                    break
            if not found:
                ttrow.append("-")
        truthtable.append((mux.arcs[src], ttrow))
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
    defval_bits = []
    for i in range(len(word.defval)):
        if len(word.bits[i].bits) == 0:
            defval_bits.append("X")
        else:
            defval_bits.append("1" if word.defval[i] else "0")
    defval = "{}'b{}".format(len(defval_bits), "".join(reversed(defval_bits)))
    print('<p>Default value: {}</p>'.format(defval), file=f)
    print('<table class="setword">', file=f)
    trstyle = ""
    for idx in range(len(word.bits)):
        cbits = " ".join(["{}F{}B{}".format("!" if b.inv else "", b.frame, b.bit) for b in word.bits[idx].bits])
        trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
        print(
            '<tr {}><td style="padding-left: 10px; padding-right: 10px">{}[{}]</td><td style="padding-left: 10px; padding-right: 10px">{}</td></tr>'.format(
                trstyle, word.name, idx, cbits), file=f)
    print('</table>', file=f)


def nice_sort(x):
    if x == "NONE":
        return -1, ""
    else:
        n = re.findall('\d+', x)
        if len(n) > 0:
            return int("".join(n)), x
        else:
            return 0, x


def setenum_html(enum, f):
    print('<h3 id="enum_{}">Configuration Setting {}</h3>'.format(enum.name, enum.name), file=f)
    if enum.defval != "":
        print('<p>Default value: {}</p>'.format(enum.defval), file=f)
    bitset = set()
    for opt in enum.get_options():
        for bit in enum.options[opt].bits:
            bitset.add((bit.frame, bit.bit))

    bitlist = list(sorted(bitset))
    print('<table class="setenum"><tr><th>Value</th>', file=f)
    for bit in bitlist:
        print('<th style="padding-left: 10px; padding-right: 10px">F{}B{}</th>'.format(bit[0], bit[1]), file=f)
    print("</tr>", file=f)
    truthtable = []
    for opt in enum.get_options():
        ttrow = []
        for blb in bitlist:
            found = False
            for ab in enum.options[opt].bits:
                if ab.frame == blb[0] and ab.bit == blb[1]:
                    ttrow.append('0' if ab.inv else '1')
                    found = True
                    break
            if not found:
                ttrow.append("-")
        truthtable.append((opt, ttrow))
    trstyle = ""
    tt_sorted = sorted(truthtable, key=lambda x: nice_sort(x[0]))
    for (opt, ttrow) in tt_sorted:
        trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
        print('<tr {}><td>{}</td>'.format(trstyle, opt), file=f)
        for bit in ttrow:
            print('<td style="text-align: center">{}</td>'.format(bit), file=f)
        print('</td>', file=f)
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


def setenums_html(db, f):
    enums = db.get_settings_enums()
    for name in sorted(enums):
        enum = db.get_data_for_enum(name)
        setenum_html(enum, f)


def fixed_conns_html(db, f):
    conns = db.get_fixed_conns()
    if len(conns) > 0:
        print("<h3>Fixed Connections</h3>", file=f)
        print('<table class="fconn" style="border-spacing:0"><tr><th>Source</th><th></th><th>Sink</th></tr>', file=f)
        trstyle = ""
        sorted_conns = sorted(conns, key=lambda x: re.sub(r"^([NESW]\d+)+_", "", x.sink))
        for conn in sorted_conns:
            trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
            print(
                """<tr {}><td style="padding-left: 10px; padding-right: 10px; margin-left: 0px;">{}</td><td>&rarr;</td>
                <td style="padding-left: 10px; padding-right: 10px">{}</td></tr>""".format(
                    trstyle, conn.source, conn.sink), file=f)
        print('</table>', file=f)


colours = {"A": "#88FFFF", "B": "#FF88FF", "C": "#8888FF", "D": "#FFFF88", "M": "#FFBBBB", "H": "#BBBBFF",
           "V": "#FFFFBB"}


def get_bit_info(frame, bit):
    if (frame, bit) in bitmap:
        group = bitmap[(frame, bit)]
        if group.startswith("mux"):
            label = group.split("_")[-1][0]
            if label == "J":
                label = group.split("_")[-1][1]
            if label in colours:
                colour = colours[label]
            else:
                colour = "#FF8888"
        elif group.startswith("enum") or group.startswith("word"):
            label = re.split("[_.]", group)[-1][0]
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
            title = "F{}B{}".format(frame, bit)
            if (frame, bit) in labels:
                for lab in sorted(labels[frame, bit]):
                    title += "&#13;&#10;" + lab
            print("""<a href='#{}' title='{}' style='text-decoration: none; color: #000000'>
                    <div id='f{}b{}' style='height: 100%; background-color: {}; width: 12px' class='grp_{}'
                    onmouseover='mov(event);' onmouseout='mou(event);'>{}</div></a></td>""".format(
                group, title, frame, bit, colour, group, label), file=f)
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
    global bitmap, labels
    bitmap = dict(dict())
    labels = dict(dict())
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
    pytrellis.load_database(database.get_db_root())
    tdb = pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(args.family, args.device, args.tile))
    ch = pytrellis.Chip(args.device)
    ti = ch.get_tiles_by_type(args.tile)[0].info
    find_bits(tdb)
    bit_grid_html(ti, f)
    muxes_html(tdb, f)
    setwords_html(tdb, f)
    setenums_html(tdb, f)
    fixed_conns_html(tdb, f)
    print("""</body></html>""", file=f)


if __name__ == "__main__":
    main(sys.argv)
