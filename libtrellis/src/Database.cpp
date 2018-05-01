#include "Database.hpp"
#include "Chip.hpp"
#include "Tile.hpp"
#include "Util.hpp"
#include <iostream>
#include <boost/optional.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <stdexcept>

namespace pt = boost::property_tree;

namespace Trellis {
static string db_root = "";
static pt::ptree devices_info;

void load_database(string root) {
    db_root = root;
    pt::read_json(root + "/" + "devices.json", devices_info);
}

// Iterate through all family and device permutations
// T should return true in case of a match
template<typename T>
boost::optional<DeviceLocator> find_device_generic(T f) {
    for (const pt::ptree::value_type &family : devices_info.get_child("families")) {
        for (const pt::ptree::value_type &dev : family.second.get_child("devices")) {
            bool res = f(dev.first, dev.second);
            if (res)
                return boost::make_optional(DeviceLocator{family.first, dev.first});
        }
    }
    return boost::optional<DeviceLocator>();
}

DeviceLocator find_device_by_name(string name) {
    auto found = find_device_generic([name](const string &n, const pt::ptree &p) -> bool { return n == name; });
    if (!found)
        throw runtime_error("no device in database with name " + name);
    return *found;
}

// Hex is not allowed in JSON, to avoid an ugly decimal integer use a string instead
// But we need to parse this back to a uint32_t
uint32_t parse_uint32(string str) {
    return uint32_t(strtoul(str.c_str(), nullptr, 0));
}

DeviceLocator find_device_by_idcode(uint32_t idcode) {
    auto found = find_device_generic([idcode](const string &n, const pt::ptree &p) -> bool {
        return parse_uint32(p.get<string>("idcode")) == idcode;
    });
    if (!found)
        throw runtime_error("no device in database with IDCODE " + uint32_to_hexstr(idcode));
    return *found;
}

ChipInfo get_chip_info(const DeviceLocator &part) {
    pt::ptree dev = devices_info.get_child("families").get_child(part.family).get_child("devices").get_child(
            part.device);
    ChipInfo ci;
    ci.family = part.family;
    ci.name = part.device;
    ci.num_frames = dev.get<int>("frames");
    ci.bits_per_frame = dev.get<int>("bits_per_frame");
    ci.pad_bits_after_frame = dev.get<int>("pad_bits_after_frame");
    ci.pad_bits_before_frame = dev.get<int>("pad_bits_before_frame");
    ci.idcode = parse_uint32(dev.get<string>("idcode"));
    return ci;
}

vector<TileInfo> get_device_tilegrid(const DeviceLocator &part) {
    vector<TileInfo> tilesInfo;
    assert(db_root != "");
    string tilegrid_path = db_root + "/" + part.family + "/" + part.device + "/tilegrid.json";
    pt::ptree tg;
    pt::read_json(tilegrid_path, tg);
    for (const pt::ptree::value_type &tile : tg) {
        TileInfo ti;
        ti.name = tile.first;
        ti.num_frames = size_t(tile.second.get<int>("cols"));
        ti.bits_per_frame = size_t(tile.second.get<int>("rows"));
        ti.bit_offset = size_t(tile.second.get<int>("start_bit"));
        ti.frame_offset = size_t(tile.second.get<int>("start_frame"));
        for (const pt::ptree::value_type &site : tg.get_child("sites")) {
            SiteInfo si;
            si.type = site.second.get<string>("name");
            si.col = site.second.get<int>("pos_col");
            si.row = site.second.get<int>("pos_row");
            ti.sites.push_back(si);
        }
        tilesInfo.push_back(ti);
    }
    return tilesInfo;
}


}
