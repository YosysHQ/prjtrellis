#!/usr/bin/env python3
import json
import sys
import timing_dbs


def html_for_cell(cellname, cell, html):
    def proc_pin(pin):
        if type(pin) is list:
            return " ".join(pin)
        else:
            return pin

    iopaths = []
    setupholds = []
    widths = []
    for entry in cell:
        if entry["type"] == "IOPath":
            iopaths.append((
                proc_pin(entry["from_pin"]), proc_pin(entry["to_pin"]),
                tuple(entry["rising"]), tuple(entry["rising"])
            ))
        elif entry["type"] == "SetupHold":
            print(entry["pin"])
            setupholds.append((
                proc_pin(entry["clock"]), proc_pin(entry["pin"]),
                tuple(entry["setup"]), tuple(entry["hold"])
            ))
        elif entry["type"] == "Width":
            widths.append((
                proc_pin(entry["clock"]), tuple(entry["width"])
            ))
        else:
            assert False

    iopaths.sort()
    setupholds.sort()
    widths.sort()
    print("<a name='{}'/>".format(cellname), file=html)
    print("<h2>{}</h2>".format(cellname), file=html)
    if len(iopaths) > 0:
        print("<h3>Propagation Delays</h3>", file=html)
        print("<table width='800'>", file=html)
        print("<tbody>", file=html)
        print("<tr><th rowspan='2'>From Port</th><th rowspan='2'>To Port</th>", file=html)
        print("<th colspan='3'>Low-High Transition (ps)</th><th colspan='3'>High-Low Transition (ps)</th></tr>", file=html)
        print("<tr><th>Min</th><th>Typ</th><th>Max</th><th>Min</th><th>Typ</th><th>Max</th></tr>", file=html)

        trstyle = ""
        for path in iopaths:
            from_pin, to_pin, rising, falling = path
            trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
            print("<tr {}>".format(trstyle), file=html)
            print("<td>{}</td><td>{}</td>".format(from_pin, to_pin), file=html)
            print("<td>{}</td><td>{}</td><td>{}</td>".format(rising[0], rising[1], rising[2]), file=html)
            print("<td>{}</td><td>{}</td><td>{}</td>".format(falling[0], falling[1], falling[2]), file=html)
            print("</tr>", file=html)
        print("</tbody>", file=html)
        print("</table>", file=html)

    print("<hr/>", file=html)


def make_cell_timing_html(dbfile, family, grade, htmlfile):
    with open(dbfile, 'r') as f:
        db = json.load(f)
    with open(htmlfile, 'w') as html:
        print("<html>", file=html)
        print("<head>", file=html)
        print("<title>{} Speed Grade -{} Cell Timings</title>".format(family, grade), file=html)
        print("</head>", file=html)
        print("<body>", file=html)
        print("<h1>{} Speed Grade -{} Cell Timings</h1>".format(family, grade), file=html)
        print("<h3>Contents</h3>", file=html)
        print("<ul>", file=html)
        for cell in sorted(db.keys()):
            print("<a href='#{}'>{}</a>".format(cell, cell), file=html)
        print("</ul>", file=html)
        print("<hr/>", file=html)
        for cellname in sorted(db.keys()):
            html_for_cell(cellname, db[cellname], html)
        print("</body>", file=html)
        print("</html>", file=html)


def main(argv):
    if len(argv) < 3:
        print("./cell_html.py grade out.html")
    make_cell_timing_html(timing_dbs.cells_db_path("ECP5", argv[1]), "ECP5", argv[1], argv[2])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
