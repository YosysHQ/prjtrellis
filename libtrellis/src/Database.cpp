#include "Database.hpp"
#include "Chip.hpp"
#include "Tile.hpp"
#include "Util.hpp"
#include <iostream>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>

namespace pt = boost::property_tree;

namespace Trellis {
static string db_root = "";
static pt::ptree devices_info;

void load_database(string root) {
    db_root = root;
    pt::read_json(root + "/" + "devices.json", devices_info);
}

DeviceLocator find_device_by_name(string name) {
    // TODO
}

}
