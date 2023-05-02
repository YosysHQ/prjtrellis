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

static const regex tile_clk_dummy_re(R"(CLK_DUMMY(\d+))");
static const regex tile_clk_dummy_b_re(R"(CLK_DUMMY_PICB)");
static const regex tile_clk_dummy_t_re(R"(CLK_DUMMY_PICT)");

// Given the zero-indexed max chip_size, return the zero-indexed
// center. Mainly for MachXO2, it is based on the location of the entry
// to global routing (CENTER_EBR). LCMXO2-256/640 do not have CENTER_EBR
// in that case we take location of internal DCCs row (at bottom CIB).
// TODO: Make const.
map<pair<int, int>, pair<int, int>> center_map = {
    // LCMXO2-256
    {make_pair(7, 9), make_pair(6, 4)},
    // LCMXO2-640
    {make_pair(8, 17), make_pair(7, 7)},
    // LCMXO2-1200, LCMXO3-1300
    {make_pair(12, 21), make_pair(6, 12)},
    // LCMXO2-2000, LCMXO3-2100
    {make_pair(15, 25), make_pair(8, 13)},
    // LCMXO2-4000, LCMXO3-4300
    {make_pair(22, 31), make_pair(11, 15)},
    // LCMXO2-7000, LCMXO3-6900
    {make_pair(27, 40), make_pair(13, 18)},
    // LCMXO3-9400
    {make_pair(31, 48), make_pair(15, 24)},
};

map<pair<int, int>, int> clk_col = {
    // LCMXO256
    {make_pair(9, 5), 2},
    // LCMXO640
    {make_pair(11, 9), 4},
    // LCMXO1200
    {make_pair(16, 11), 5},
    // LCMXO2280
    {make_pair(20, 16), 8},
};

// Universal function to get a zero-indexed row/column pair.
pair<int, int> get_row_col_pair_from_chipsize(string name, pair<int, int> chip_size, int row_bias, int col_bias) {
    smatch m;

    // Special-cases... CENTER30 will match wrong regex. Only on 7000HC,
    // this position is a best-guess.
    if((name.find("CENTER30") != std::string::npos) && (chip_size == make_pair(27, 40))) {
        return make_pair(20, center_map[chip_size].second);
    } else if(name.find("CENTER33") != std::string::npos) { // LCMXO3-9400
        return make_pair(8, center_map[chip_size].second);
    } else if(name.find("CENTER35") != std::string::npos) { // LCMXO3-9400
        return make_pair(22, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_clk_dummy_t_re)) {
        return make_pair(0, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_clk_dummy_b_re)) {
        return make_pair(chip_size.first, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_clk_dummy_re)) {
        return make_pair(stoi(m.str(1)) - row_bias, center_map[chip_size].second);
    } else if(name.find("CLK") == 0 && name.find("_2K") != std::string::npos) {
        return make_pair(stoi(name.substr(7)) - row_bias, clk_col[chip_size]);
    } else if(name.find("CLK") == 0) {
        return make_pair(stoi(name.substr(4)) - row_bias, clk_col[chip_size]);
    } else if(name.find("EBR") != std::string::npos && regex_search(name, m, tile_rxcx_re) && row_bias==1) {
        // MachXO only - EBR_RxxC0 should be on position 1
        return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias + 1);
    } else if(regex_search(name, m, tile_rxcx_re)) {
        if (chip_size == make_pair(22, 31)) {
            if ((stoi(m.str(2)) - col_bias) > 31) // FIX: LCMXO3D-4300
                return make_pair(stoi(m.str(1)), stoi(m.str(2)) - col_bias - 1);
        }
        return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
    } else if(regex_search(name, m, tile_centert_re)) {
        return make_pair(0, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_centerb_re)) {
        return make_pair(chip_size.first, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_centerebr_re)) {
        return make_pair(center_map[chip_size].first, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_center_re)) {
        return make_pair(stoi(m.str(1)) - row_bias, center_map[chip_size].second);
    } else if(regex_search(name, m, tile_t_re)) {
        return make_pair(0, stoi(m.str(1)) - col_bias);
    } else if(regex_search(name, m, tile_b_re)) {
        return make_pair(chip_size.first, stoi(m.str(1)) - col_bias);
    } else if(regex_search(name, m, tile_l_re)) {
        return make_pair(stoi(m.str(1)) - row_bias, 0);
    } else if(regex_search(name, m, tile_r_re)) {
        return make_pair(stoi(m.str(1)) - row_bias, chip_size.second);
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
