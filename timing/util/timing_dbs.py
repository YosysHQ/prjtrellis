import database
from os import path


def cells_db_path(family, speedgrade):
    return path.join(database.get_db_root(), family, "timing", "speed_{}".format(speedgrade), "cells.json")
