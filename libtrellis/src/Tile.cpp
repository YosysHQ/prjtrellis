#include "Tile.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "BitDatabase.hpp"
#include "TileConfig.hpp"
#include "Util.hpp"

namespace Trellis {
// Regex to extract row/column from a tile name
static const regex tile_rxcx_re(R"(R(\d+)C(\d+))");

// Universal function to get a zero-indexed row/column pair.
pair<int, int> get_row_col_pair_from_chipsize(string name, pair<int, int> chip_size, int bias) {
    smatch m;
    bool match;

    match = regex_search(name, m, tile_rxcx_re);
    if(match) {
        return make_pair(stoi(m.str(1)), stoi(m.str(2)));
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
