#ifndef LIBTRELLIS_CHIP_HPP
#define LIBTRELLIS_CHIP_HPP

#include <string>
#include <memory>
#include <vector>
#include <cstdint>
#include <map>
#include <set>
#include "CRAM.hpp"

using namespace std;
namespace Trellis {

// Basic information about a chip that may be needed elsewhere
struct ChipInfo
{
    string name;
    string family;
    uint32_t idcode;
    int num_frames;
    int bits_per_frame;
    int pad_bits_before_frame;
    int pad_bits_after_frame;
    // 0-based.
    int max_row;
    int max_col;
    // Trellis uses 0-based indexing, but some devices don't.
    int col_bias;
};

// Information about the global networks in a chip
struct GlobalRegion
{
    string name;
    int x0, y0, x1, y1;

    bool matches(int row, int col) const;
};

inline bool operator==(const GlobalRegion &a, const GlobalRegion &b)
{
    return (a.name == b.name) && (a.x0 == b.x0) && (a.x1 == b.x1) && (a.y0 == b.y0) && (a.y1 == b.y1);
}

struct TapSegment
{
    int tap_col;
    int lx0, lx1, rx0, rx1;

    bool matches_left(int row, int col) const;

    bool matches_right(int row, int col) const;
};

inline bool operator==(const TapSegment &a, const TapSegment &b)
{
    return (a.tap_col == b.tap_col) && (a.lx0 == b.lx0) && (a.lx1 == b.lx1) && (a.rx0 == b.rx0) && (a.rx1 == b.rx1);
}

struct TapDriver
{
    int col;
    enum TapDir
    {
        LEFT,
        RIGHT
    } dir;
};

struct SpineSegment
{
    int tap_col;
    string quadrant;
    int spine_row, spine_col;
};

struct GlobalsInfo
{
    vector<GlobalRegion> quadrants;
    vector<TapSegment> tapsegs;
    vector<SpineSegment> spinesegs;

    string get_quadrant(int row, int col) const;

    TapDriver get_tap_driver(int row, int col) const;

    pair<int, int> get_spine_driver(std::string quadrant, int col);
};

class Tile;

// A difference between two Chips
// A list of pairs mapping between tile identifier (name:type) and tile difference
typedef map<string, CRAMDelta> ChipDelta;

class RoutingGraph;

class Chip
{
public:
    // Construct a chip by looking up part name
    explicit Chip(string name);

    // Construct a chip by looking up device ID
    explicit Chip(uint32_t idcode);

    // Construct a chip from a ChipInfo
    explicit Chip(const ChipInfo &info);

    // Basic information about a chip
    ChipInfo info;

    // The chip's configuration memory
    CRAM cram;

    // Tile access
    shared_ptr<Tile> get_tile_by_name(string name);

    vector<shared_ptr<Tile>> get_tiles_by_position(int row, int col);

    vector<shared_ptr<Tile>> get_tiles_by_type(string type);

    vector<shared_ptr<Tile>> get_all_tiles();

    string get_tile_by_position_and_type(int row, int col, string type);

    string get_tile_by_position_and_type(int row, int col, set<string> type);

    // Map tile name to a tile reference
    map<string, shared_ptr<Tile>> tiles;

    // Miscellaneous information
    uint32_t usercode = 0x0;
    uint32_t ctrl0 = 0x40000000;
    vector<string> metadata;

    // Get max row and column
    int get_max_row() const;

    int get_max_col() const;

    // Build the routing graph for the chip
    shared_ptr<RoutingGraph> get_routing_graph();

    vector<vector<vector<pair<string, string>>>> tiles_at_location;

    // Block RAM initialisation (WIP)
    map<uint16_t, vector<uint16_t>> bram_data;

    // Globals data
    GlobalsInfo global_data;
};

ChipDelta operator-(const Chip &a, const Chip &b);
}

#endif //LIBTRELLIS_CHIP_HPP
