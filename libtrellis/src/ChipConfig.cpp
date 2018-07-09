#include "ChipConfig.hpp"
#include "Chip.hpp"
#include "BitDatabase.hpp"
#include "Database.hpp"
#include "Tile.hpp"
#include <sstream>
#include <iostream>

namespace Trellis {

string ChipConfig::to_string() const
{
    stringstream ss;
    ss << ".device " << chip_name << endl << endl;
    for (const auto &meta : metadata)
        ss << ".comment " << meta << endl;
    ss << endl;
    for (const auto &tile : tiles) {
        if (!tile.second.empty()) {
            ss << ".tile " << tile.first << endl;
            ss << tile.second;
            ss << endl;
        }
    }
    return ss.str();
}

ChipConfig ChipConfig::from_string(const string &config)
{
    stringstream ss(config);
    ChipConfig cc;
    while (!skip_check_eof(ss)) {
        std::string verb;
        ss >> verb;
        if (verb == ".device") {
            ss >> cc.chip_name;
        } else if (verb == ".comment") {
            std::string line;
            getline(ss, line);
            cc.metadata.push_back(line);
        } else if (verb == ".tile") {
            std::string tilename;
            ss >> tilename;
            TileConfig tc;
            ss >> tc;
            cc.tiles[tilename] = tc;
        } else {
            throw runtime_error("unrecognised config entry " + verb);
        }
    }
    return cc;
}

Chip ChipConfig::to_chip() const
{
    Chip c(chip_name);
    c.metadata = metadata;
    for (auto tile_entry : c.tiles) {
        auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, tile_entry.second->info.type});
        if (tiles.find(tile_entry.first) != tiles.end()) {
            tile_db->config_to_tile_cram(tiles.at(tile_entry.first), tile_entry.second->cram);
        } else {
            // Empty config sets default values (not always zero, e.g. in IO tiles)
            tile_db->config_to_tile_cram(TileConfig(), tile_entry.second->cram);
        }
    }
    return c;
}

ChipConfig ChipConfig::from_chip(const Chip &chip)
{
    ChipConfig cc;
    cc.chip_name = chip.info.name;
    cc.metadata = chip.metadata;
    for (auto tile : chip.tiles) {
        auto tile_db = get_tile_bitdata(TileLocator{chip.info.family, chip.info.name, tile.second->info.type});
        cc.tiles[tile.first] = tile_db->tile_cram_to_config(tile.second->cram);
    }
    return cc;
}

}
