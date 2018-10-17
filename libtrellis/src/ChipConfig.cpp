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
    for (const auto &bram : bram_data) {
        ss << ".bram_init " << bram.first << endl;
        ios_base::fmtflags f( ss.flags() );
        for (size_t i = 0; i < bram.second.size(); i++) {
            ss << setw(3) << setfill('0') << hex << bram.second.at(i);
            if (i % 8 == 7)
                ss << endl;
            else
                ss << " ";
        }
        ss.flags(f);
        ss << endl;
    }
    for (const auto &tg : tilegroups) {
        ss << ".tile_group";
        for (const auto &tile : tg.tiles) {
            ss << " " << tile;
        }
        ss << endl;
        ss << tg.config;
        ss << endl;
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
            ss.get(); //skip space
            getline(ss, line);
            cc.metadata.push_back(line);
        } else if (verb == ".tile") {
            std::string tilename;
            ss >> tilename;
            TileConfig tc;
            ss >> tc;
            cc.tiles[tilename] = tc;
        } else if (verb == ".bram_init") {
            uint16_t bram;
            ss >> bram;
            ios_base::fmtflags f(ss.flags());
            while (!skip_check_eor(ss)) {
                uint16_t value;
                ss >> hex >> value;
                cc.bram_data[bram].push_back(value);
            }
            ss.flags(f);
        } else if (verb == ".tile_group") {
            TileGroup tg;
            std::string line;
            getline(ss, line);
            std::stringstream ss2(line);

            std::string tile;
            while (ss2) {
                ss2 >> tile;
                tg.tiles.push_back(tile);
            }
            ss >> tg.config;
            cc.tilegroups.push_back(tg);
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
    c.bram_data = bram_data;
    set<string> processed_tiles;
    for (auto tile_entry : c.tiles) {
        auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, tile_entry.second->info.type});
        if (tiles.find(tile_entry.first) != tiles.end()) {
            tile_db->config_to_tile_cram(tiles.at(tile_entry.first), tile_entry.second->cram);
        } else {
            // Empty config sets default values (not always zero, e.g. in IO tiles)
            tile_db->config_to_tile_cram(TileConfig(), tile_entry.second->cram);
        }
        processed_tiles.insert(tile_entry.first);
    }

    for (const auto &tilegroup : tilegroups) {
        set<string> matched;
        for (const auto &tilename : tilegroup.tiles) {
            auto tile = c.tiles.at(tilename);
            auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, tile->info.type});
            tile_db->config_to_tile_cram(tilegroup.config, tile->cram, true, &matched);
        }
        for (const auto &word : tilegroup.config.cwords)
            if (!matched.count(word.name))
                throw runtime_error("config word " + word.name + " matched in no tilegroup tiles");
        for (const auto &cenum : tilegroup.config.cenums)
            if (!matched.count(cenum.name))
                throw runtime_error("config enum " + cenum.name + " matched in no tilegroup tiles");
    }

    for (auto &tile : tiles) {
        if (!processed_tiles.count(tile.first)) {
            throw runtime_error("tile " + tile.first + " does not exist in chip " + chip_name);
        }
    }
    return c;
}

ChipConfig ChipConfig::from_chip(const Chip &chip)
{
    ChipConfig cc;
    cc.chip_name = chip.info.name;
    cc.metadata = chip.metadata;
    cc.bram_data = chip.bram_data;
    for (auto tile : chip.tiles) {
        auto tile_db = get_tile_bitdata(TileLocator{chip.info.family, chip.info.name, tile.second->info.type});
        cc.tiles[tile.first] = tile_db->tile_cram_to_config(tile.second->cram);
    }
    return cc;
}

}
