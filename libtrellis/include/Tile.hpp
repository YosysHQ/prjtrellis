#ifndef LIBTRELLIS_TILE_HPP
#define LIBTRELLIS_TILE_HPP

#include <string>
#include <cstdint>
#include <utility>
#include <regex>
#include <cassert>
#include "CRAM.hpp"

namespace Trellis {

// Regex to extract row/column from a tile name
static const regex tile_row_col_re(R"(R(\d+)C(\d+))");

// Basic information about a site
struct SiteInfo {
    string type;
    int row;
    int col;
};

// Reference to a bit location
struct TileBit {
    size_t row;
    size_t bit;
};

// Basic information about a tile
struct TileInfo {
    string name;
    string type;
    size_t num_frames;
    size_t bits_per_frame;
    size_t frame_offset;
    size_t bit_offset;
    vector<SiteInfo> sites;

    inline pair<int, int> get_row_col() const {
        smatch m;
        assert(regex_search(name, m, tile_row_col_re));
        return make_pair(stoi(m.str(1)), stoi(m.str(2)));
    };
};

}


#endif //LIBTRELLIS_TILE_HPP
