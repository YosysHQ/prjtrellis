#!/usr/bin/env python3
import parse_sdf
from os import path
import json
import sys


def include_cell(name, type):
    return type.isupper() and "_" not in type


def rewrite_celltype(name, type):
    return type


def rewrite_pin(name, type, pin):
    return pin


def tupleise(x):
    if type(x) is list:
        return tuple(tupleise(_) for _ in x)
    elif type(x) is tuple:
        return tuple(tupleise(_) for _ in x)
    elif type(x) is dict:
        return "dict", tuple([(k, tupleise(v)) for k, v in sorted(x.items())])
    else:
        return x


def load_database(dbfile):
    if not path.exists(dbfile):
        database = {}
    else:
        database = {}
        with open(dbfile, 'r') as dbf:
            jsondb = json.load(dbf)
        for cell, cdata in jsondb.items():
            database[cell] = set()
            for item in cdata:
                database[cell].add(tupleise(item))
    return database


def make_key(x):
    if type(x) is tuple:
        return ",".join(make_key(_) for _ in x)
    else:
        return str(x)


def save_database(dbfile, database):
    jdb = {}
    for cell, cdata in database.items():
        jcdata = []
        for dtype, dat in sorted(cdata, key=lambda x: make_key(x)):
            assert dtype == "dict"
            jcdata.append({k: v for k, v in dat})
        jdb[cell] = jcdata
    with open(dbfile, 'w') as dbf:
        json.dump(jdb, dbf, indent=4, sort_keys=True)


def delay_tuple(delay):
    return delay.minv, delay.typv, delay.maxv


def add_sdf_to_database(dbfile, sdffile, include_cell_predicate=include_cell, rewrite_cell_func=rewrite_celltype,
                        rewrite_pin_func=rewrite_pin):
    db = load_database(dbfile)
    sdf = parse_sdf.parse_sdf_file(sdffile)
    for instname, cell in sdf.cells.items():
        if not include_cell_predicate(cell.inst, cell.type):
            continue
        celltype = rewrite_cell_func(cell.inst, cell.type)
        if celltype not in db:
            db[celltype] = set()
        for entry in cell.entries:
            if type(entry) is parse_sdf.IOPath:
                db[celltype].add(tupleise(
                    dict(type="IOPath", from_pin=rewrite_pin_func(cell.inst, cell.type, entry.from_pin),
                         to_pin=rewrite_pin_func(cell.inst, cell.type, entry.to_pin), rising=delay_tuple(entry.rising),
                         falling=delay_tuple(entry.falling))))
            elif type(entry) is parse_sdf.SetupHoldCheck:
                db[celltype].add(
                    tupleise(dict(type="SetupHold", pin=rewrite_pin_func(cell.inst, cell.type, entry.pin),
                                  clock=rewrite_pin_func(cell.inst, cell.type, entry.clock),
                                  setup=delay_tuple(entry.setup),
                                  hold=delay_tuple(entry.hold))))
            elif type(entry) is parse_sdf.WidthCheck:
                db[celltype].add(tupleise(dict(type="Width", clock=rewrite_pin_func(cell.inst, cell.type, entry.clock),
                                               width=delay_tuple(entry.width))))
            else:
                assert False
    save_database(dbfile, db)


def main(argv):
    if len(argv) < 3:
        print("Usage: cell_timings.py database.json design.sdf")
        return 2
    add_sdf_to_database(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
