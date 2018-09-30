import pytrellis

def main():
    pytrellis.load_database("../../database")
    db = pytrellis.get_tile_bitdata(pytrellis.TileLocator("ECP5", "LFE5U-25F", "PLC2"))
    fc = pytrellis.FixedConnection()
    fc.source = "FCO"
    fc.sink = "E1_HFIE0000"
    db.add_fixed_conn(fc)
    db.save()

if __name__ == "__main__":
    main()
