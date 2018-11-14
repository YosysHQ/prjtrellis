import sys
import json
import timing_dbs
import pip_classes


def make_interconn_timing_html(dbfile, family, grade, htmlfile):
    with open(dbfile, 'r') as f:
        db = json.load(f)
    with open(htmlfile, 'w') as html:
        print("<html>", file=html)
        print("<head>", file=html)
        print("<title>{} Speed Grade -{} Interconnect Timings</title>".format(family, grade), file=html)
        print("</head>", file=html)
        print("<body>", file=html)
        print("<h1>{} Speed Grade -{} Interconnect Timings</h1>".format(family, grade), file=html)
        print("<p>Values in red are fixed to zero by definition.</p>", file=html)
        print("<table width='800'>", file=html)
        print("<tbody>", file=html)
        print("<tr><th rowspan='2'>Pip Class</th>", file=html)
        print("<th colspan='3'>Base Delay (ps)</th><th colspan='3'>Fanout Adder (ps)</th></tr>", file=html)
        print("<tr><th>Min</th><th>Typ</th><th>Max</th><th>Min</th><th>Typ</th><th>Max</th></tr>", file=html)

        trstyle = ""
        for pipclass, pcdata in sorted(db.items()):
            trstyle = " bgcolor=\"#dddddd\"" if trstyle == "" else ""
            print("<tr {}>".format(trstyle), file=html)
            print("<td>{}</td>".format(pipclass), file=html)
            ds = "style='color: red;'" if pip_classes.force_zero_delay_pip(pipclass) else ""
            fs = "style='color: red;'" if pip_classes.force_zero_fanout_pip(pipclass) else ""
            print("<td {}>{:.0f}</td><td {}>{:.0f}</td><td {}>{:.0f}</td>".format(ds, pcdata["delay"][0], ds, pcdata["delay"][1], ds, pcdata["delay"][2]), file=html)
            print("<td {}>{:.0f}</td><td {}>{:.0f}</td><td {}>{:.0f}</td>".format(fs, pcdata["fanout"][0], fs, pcdata["fanout"][1], fs, pcdata["fanout"][2]), file=html)
            print("</tr>", file=html)
        print("</tbody>", file=html)
        print("</table>", file=html)
        print("</body>", file=html)
        print("</html>", file=html)


def main(argv):
    if len(argv) < 3:
        print("./interconnect_html.py grade out.html")
    make_cell_timing_html(timing_dbs.interconnect_db_path("ECP5", argv[1]), "ECP5", argv[1], argv[2])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
