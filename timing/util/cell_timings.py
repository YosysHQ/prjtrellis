#!/usr/bin/env python3
import parse_sdf
from os import path
import json
import sys


def include_cell(name, type):
    return type.isupper() and "_" not in type


def rewrite_celltype(name, type):
    return type


def tupleise(x):
    if type(x) is list:
        return tuple([tupleise(_) for _ in x])
    elif type(x) is tuple:
        return tuple([tupleise(_) for _ in x])
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


def save_database(dbfile, database):
    jdb = {}
    for cell, cdata in database.items():
        jdb[cell] = list(cdata)
    with open(dbfile, 'w') as dbf:
        json.dump(jdb, dbf, indent=4, sort_keys=True)


def delay_tuple(delay):
    return delay.minv, delay.typv, delay.maxv


def add_sdf_to_database(dbfile, sdffile, include_cell_predicate=include_cell, rewrite_cell_func=rewrite_celltype):
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
                db[celltype].add(("IOPath", tupleise(entry.from_pin), tupleise(entry.to_pin), delay_tuple(entry.rising),
                                  delay_tuple(entry.falling)))
            elif type(entry) is parse_sdf.SetupHoldCheck:
                db[celltype].add(("SetupHold", tupleise(entry.pin), tupleise(entry.clock), delay_tuple(entry.setup),
                                  delay_tuple(entry.hold)))
            elif type(entry) is parse_sdf.WidthCheck:
                db[celltype].add(("Width", tupleise(entry.clock), delay_tuple(entry.width)))
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
