#include "Tile.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "BitDatabase.hpp"
#include "TileConfig.hpp"
#include "Util.hpp"

namespace Trellis {
// Regexes to extract row/column from a tile name.
static const regex tile_rxcx_re(R"(R(\d+)C(\d+))");

// MachXO2-specific, in order of precedence (otherwise, e.g.
// CENTER_EBR matches r_regex)
static const regex tile_center_re(R"(CENTER(\d+))");
static const regex tile_centerb_re(R"(CENTER_B)");
static const regex tile_centert_re(R"(CENTER_T)");
static const regex tile_centerebr_re(R"(CENTER_EBR(\d+))");
static const regex tile_t_re(R"([A-Za-z0-9_]*T(\d+))");
static const regex tile_b_re(R"([A-Za-z0-9_]*B(\d+))");
static const regex tile_l_re(R"([A-Za-z0-9_]*L(\d+))");
static const regex tile_r_re(R"([A-Za-z0-9_]*R(\d+))");

// Given the zero-indexed max chip_size, return the zero-indexed
// center. Mainly for MachXO2, it is based on the location of the entry
// to global routing.
// TODO: Make const.
map<pair<int, int>, pair<int, int>> center_map = {
    // 256HC
    {make_pair(7, 9), make_pair(3, 4)},
    // 640HC
    {make_pair(8, 17), make_pair(3, 7)},
    // 1200HC
    {make_pair(12, 21), make_pair(6, 12)}
};

// Universal function to get a zero-indexed row/column pair.
pair<int, int> get_row_col_pair_from_chipsize(string name, pair<int, int> chip_size, int bias) {
    smatch m;

    if(regex_search(name, m, tile_rxcx_re)) {
        return make_pair(stoi(m.str(1)), stoi(m.str(2)) - bias);
    } else if(regex_search(name, m, tile_centert_re)) {
        return make_pair(0, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_centerb_re)) {
        return make_pair(chip_size.first, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_centerebr_re)) {
        // TODO: This may not apply to devices larger than 1200.
        return make_pair(center_map[chip_size].first, stoi(m.str(1)) - bias);
    } else if(regex_search(name, m, tile_center_re)) {
        return make_pair(stoi(m.str(1)), center_map[chip_size].second);
    } else if(regex_search(name, m, tile_t_re)) {
        return make_pair(0, stoi(m.str(1)) - bias);
    } else if(regex_search(name, m, tile_b_re)) {
        return make_pair(chip_size.first, stoi(m.str(1)) - bias);
    } else if(regex_search(name, m, tile_l_re)) {
        return make_pair(stoi(m.str(1)), 0);
    } else if(regex_search(name, m, tile_r_re)) {
        return make_pair(stoi(m.str(1)), chip_size.second);
    } else {
        throw runtime_error(fmt("Could not extract position from " << name));
    }
}

Tile::Tile(Trellis::TileInfo info, Trellis::Chip &parent) : info(info), cram(parent.cram.make_view(info.frame_offset,
                                                                                                   info.bit_offset,
                                                                                                   info.num_frames,
                                                                                                   info.bits_per_frame)) {}

string Tile::dump_config() const {
    shared_ptr<TileBitDatabase> bitdb = get_tile_bitdata(TileLocator(info.family, info.device, info.type));
    TileConfig cfg = bitdb->tile_cram_to_config(cram);
    known_bits = cfg.total_known_bits;
    unknown_bits = int(cfg.cunknowns.size());
    stringstream ss;
    ss << cfg;
    return ss.str();
}

void Tile::read_config(string config) {
    shared_ptr<TileBitDatabase> bitdb = get_tile_bitdata(TileLocator(info.family, info.device, info.type));
    stringstream ss(config);
    TileConfig tcfg;
    ss >> tcfg;
    bitdb->config_to_tile_cram(tcfg, cram);
}
}
