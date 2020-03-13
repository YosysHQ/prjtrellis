#ifndef LIBTRELLIS_TILE_HPP
#define LIBTRELLIS_TILE_HPP

#include <string>
#include <iostream>
#include <cstdint>
#include <utility>
#include <regex>
#include <cassert>
#include "CRAM.hpp"

namespace Trellis {
pair<int, int> get_row_col_pair_from_chipsize(string name, pair<int, int> chip_size, int bias);

// Basic information about a site
struct SiteInfo {
    string type;
    int row;
    int col;
    // Needed for Python binding
    bool operator==(const SiteInfo &b) const {
        return (this->row == b.row) && (this->col == b.col) && (this->type == b.type);
    }
};

// Basic information about a tile
struct TileInfo {
    string family;
    string device;
    size_t max_col;
    size_t max_row;
    int col_bias;

    string name;
    string type;
    size_t num_frames;
    size_t bits_per_frame;
    size_t frame_offset;
    size_t bit_offset;
    vector<SiteInfo> sites;

    inline pair<int, int> get_row_col() const {
        auto chip_size = make_pair(int(max_row), int(max_col));
        auto row_col = get_row_col_pair_from_chipsize(name, chip_size, col_bias);
        assert(row_col <= chip_size);
        return row_col;
    };

    // Get the Lattice name
    // Tiles are identified internally as "lattice_name:type"
    // This is because the Lattice name is NOT unique, and we need tiles to have a unique identifier
    inline string get_lattice_name() const {
        return name.substr(0, name.find(':'));
    }


};

class Chip;
// Represents an actual tile
class Tile {
public:
    Tile(TileInfo info, Chip &parent);
    TileInfo info;
    CRAMView cram;

    // Dump the tile textual config as a string
    string dump_config() const;
    // Configure the tile from a string config
    void read_config(string config);
    // Set by dump_config
    mutable int known_bits = 0;
    mutable int unknown_bits = 0;
};

}


#endif //LIBTRELLIS_TILE_HPP
