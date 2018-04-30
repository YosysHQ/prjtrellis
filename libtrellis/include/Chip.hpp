#ifndef LIBTRELLIS_CHIP_HPP
#define LIBTRELLIS_CHIP_HPP

#include <string>
#include <memory>
#include <vector>
#include <cstdint>
#include <map>

#include "CRAM.hpp"

using namespace std;
namespace Trellis {

// Basic information about a chip that may be needed elsewhere
struct ChipInfo {
    string name;
    uint32_t idcode;
    int num_frames;
    int bits_per_frame;
    int pad_bits_before_frame;
    int pad_bits_after_frame;
};

class Tile;

class Chip {
public:
    // Construct a chip by looking up part name
    explicit Chip(string name);

    // Construct a chip by looking up device ID
    explicit Chip(uint32_t idcode);

    // Basic information about a chip
    const ChipInfo info;

    // The chip's configuration memory
    CRAM cram;

    // Tile access
    shared_ptr<Tile> get_tile_by_name(string name);

    vector<shared_ptr<Tile>> get_tiles_by_position(int row, int col);

    vector<shared_ptr<Tile>> get_tiles_by_type(string type);

    // Map tile name to a tile reference
    map<string, shared_ptr<Tile>> tiles;
};
}

#endif //LIBTRELLIS_CHIP_HPP
