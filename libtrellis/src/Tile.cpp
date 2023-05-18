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

static const regex viq_bot_re(R"(VIQ_BOT[0-9](\d+))");
static const regex viq_top_re(R"(VIQ_TOP[0-9](\d+))");
static const regex viq_dsp_re(R"(VIQ_DSP(\d+))");
static const regex viq_emb_re(R"(VIQ_EMB(\d+))");
static const regex viq_picb_re(R"(VIQ_PICB(\d+))");
static const regex viq_pict_re(R"(VIQ_PICT(\d+))");
static const regex viq_re(R"(VIQ(\d+))");



static const regex viq_dsp_num_re(R"(VIQ_DSP[0-9](\d+))");
static const regex viq_dspplus_re(R"(VIQ_DSPPLUS[0-9](\d+))");
static const regex viq_emb_num_re(R"(VIQ_EMB[0-9](\d+))");
static const regex viq_embplus_re(R"(VIQ_EMBPLUS[0-9A-Z](\d+))");

static const regex viq_embb_re(R"(VIQ_EMBB(\d+))");

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
    {make_pair(27, 40), make_pair(17, 18)},
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

map<pair<int, int>, int> viq_col = {
    // LFXP2-5E
    {make_pair(25, 28), 18},
    // LFXP2-8E
    {make_pair(32, 37), 18},
    // LFXP2-17E
    {make_pair(49, 46), 27},
    // LFXP2-30E
    {make_pair(61, 64), 36},
    // LFXP2-40E
    {make_pair(73, 73), 36},
};

// Universal function to get a zero-indexed row/column pair.
pair<int, int> get_row_col_pair_from_chipsize(string name, string family, pair<int, int> chip_size, int row_bias, int col_bias) {
    smatch m;

    if (family=="ECP5" || family == "LIFMD" || family == "LIFMDF") {
        // All tiles have proper prefix, no bias used
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else {
            throw runtime_error(fmt("Could not extract position from " << name));
        }
    } else if (family=="LatticeXP2" || family == "LatticeXP") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(regex_search(name, m, viq_bot_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_top_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_dsp_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_emb_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_picb_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_pict_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(name.find("BDLL") == 0) {
            return make_pair(0,0);
        } else if(name.find("TDLL") == 0) {
            return make_pair(0,0);
        } else if(name.find("CLK") == 0) {
            return make_pair(0,0);
        } else if(name.find("CONFIG") == 0) {
            return make_pair(0,0);
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
    } else if (family=="LatticeECP3") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(regex_search(name, m, tile_t_re)) {
            return make_pair(0, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_b_re)) {
            return make_pair(chip_size.first, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_l_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, 0);
        } else if(regex_search(name, m, tile_r_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, chip_size.second);
        } else {
            //throw runtime_error(fmt("Could not extract position from " << name));
            return make_pair(0,0);
        }
    } else if (family=="LatticeECP" || family=="LatticeEC") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(name.find("CLK_") == 0) {
            return make_pair(0,0);
        } else if(name.find("CLK") == 0) {
            //return make_pair(stoi(name.substr(5)) - row_bias, 0);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_bot_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_top_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_dspplus_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_dsp_num_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_embplus_re)) {
            //return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_emb_num_re)) {
            //return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_picb_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_pict_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
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
            //return make_pair(0,0);
        }
    } else if (family=="LatticeECP2") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(name.find("CLK_") == 0) {
            return make_pair(0,0);
        } else if(name.find("CLK") == 0) {
            //return make_pair(stoi(name.substr(5)) - row_bias, 0);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_bot_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_top_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_dspplus_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_dsp_num_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_embplus_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_emb_num_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_picb_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_pict_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
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
            //return make_pair(0,0);
        }
    } else if (family=="LatticeECP2M") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(name.find("CLK") == 0) {
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_bot_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_top_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_dsp_re)) {
            //return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_emb_re)) {
            //return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_embb_re)) {
            //return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
            return make_pair(0,0);
        } else if(regex_search(name, m, viq_picb_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_pict_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, viq_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, viq_col[chip_size]);
        } else if(regex_search(name, m, tile_t_re)) {
            return make_pair(0, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_b_re)) {
            return make_pair(chip_size.first, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_l_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, 0);
        } else if(regex_search(name, m, tile_r_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, chip_size.second);
        } else {
            //throw runtime_error(fmt("Could not extract position from " << name));
            return make_pair(0,0);
        }
    } else if (family=="MachXO") {
        if(regex_search(name, m, tile_clk_dummy_t_re)) {
            return make_pair(0, clk_col[chip_size]);
        } else if(regex_search(name, m, tile_clk_dummy_b_re)) {
            return make_pair(chip_size.first, clk_col[chip_size]);
        } else if(regex_search(name, m, tile_clk_dummy_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, clk_col[chip_size]);
        } else if(name.find("CLK") == 0 && name.find("_2K") != std::string::npos) {
            return make_pair(stoi(name.substr(7)) - row_bias, clk_col[chip_size]);
        } else if(name.find("CLK") == 0) {
            return make_pair(stoi(name.substr(4)) - row_bias, clk_col[chip_size]);
        } else if(name.find("EBR") != std::string::npos && regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias + 1);
        } else if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
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
    } else if (family.length()>6 && family.substr(0,6)=="MachXO") { // MachXO2, MachXO3, MachXO3D
        // Special-cases... CENTER30 will match wrong regex. Only on 7000HC,
        // this position is a best-guess.
        if((name.find("CENTER30") != std::string::npos) && (chip_size == make_pair(27, 40))) {
            return make_pair(20, center_map[chip_size].second);
        } else if(name.find("CENTER33") != std::string::npos) { // LCMXO3-9400
            return make_pair(8, center_map[chip_size].second);
        } else if(name.find("CENTER35") != std::string::npos) { // LCMXO3-9400
            return make_pair(22, center_map[chip_size].second);
        } else if(regex_search(name, m, tile_rxcx_re)) {
            int col = stoi(m.str(2)) - col_bias;
            if (col > chip_size.second) col--; // FIX: LCMXO3D-4300
            return make_pair(stoi(m.str(1)) - row_bias, col);
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
    } else if(family == "LatticeSC") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(name.find("HIQ") == 0) {
            return make_pair(0,0);
        } else if(regex_search(name, m, tile_t_re)) {
            return make_pair(0, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_b_re)) {
            return make_pair(chip_size.first, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_l_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, 0);
        } else if(regex_search(name, m, tile_r_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, chip_size.second);
        } else {
            return make_pair(0,0);
        }
    } else if(family == "PlatformManager" || family == "PlatformManager2") {
        if(regex_search(name, m, tile_rxcx_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, stoi(m.str(2)) - col_bias);
        } else if(regex_search(name, m, tile_t_re)) {
            return make_pair(0, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_b_re)) {
            return make_pair(chip_size.first, stoi(m.str(1)) - col_bias);
        } else if(regex_search(name, m, tile_l_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, 0);
        } else if(regex_search(name, m, tile_r_re)) {
            return make_pair(stoi(m.str(1)) - row_bias, chip_size.second);
        } else {
            //throw runtime_error(fmt("Could not extract position from " << name));
            return make_pair(0,0);
        }
    } else {
        throw runtime_error(fmt("Unknown chip family: " + family));
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
