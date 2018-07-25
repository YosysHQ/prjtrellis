#ifndef LIBTRELLIS_DATABASE_HPP
#define LIBTRELLIS_DATABASE_HPP

#include <string>
#include <cstdint>
#include <vector>
#include <unordered_map>
#include <memory>
using namespace std;

namespace Trellis {
// This MUST be called before any operations (such as creating a Chip or reading a bitstream)
// that require database access.
void load_database(string root);

// Locator for a given FPGA (formed of family and device)
struct DeviceLocator {
    string family;
    string device;
};

// Locator for a given tile type (formed of family, device and tile type)
struct TileLocator {
    inline TileLocator() {};
    inline TileLocator(string f, string d, string t) : family(f), device(d), tiletype(t) {};
    string family;
    string device;
    string tiletype;
};

inline bool operator==(const TileLocator &a, const TileLocator &b) {
    return (a.family == b.family) && (a.device == b.device) && (a.tiletype == b.tiletype);
}

// Search the device list by part name
DeviceLocator find_device_by_name(string name);

// Search the device list by ID
DeviceLocator find_device_by_idcode(uint32_t idcode);

struct ChipInfo;

// Obtain basic information about a device
ChipInfo get_chip_info(const DeviceLocator &part);

struct GlobalsInfo;

// Obtain global network information for a chip
GlobalsInfo get_global_info(const DeviceLocator &part);

// Obtain the tilegrid for a part
struct TileInfo;

vector<TileInfo> get_device_tilegrid(const DeviceLocator &part);

// Obtain the BitDatabase for a device/tile combination
// BitDatabases are a singleton
class TileBitDatabase;
shared_ptr<TileBitDatabase> get_tile_bitdata(const TileLocator &tile);

}

// Hash function for TileLocator
namespace std {
template<> struct hash<Trellis::TileLocator> {
public:
    inline size_t operator()(const Trellis::TileLocator &tile) const {
        hash<string> hash_fn;
        return hash_fn(tile.family) + hash_fn(tile.device) + hash_fn(tile.tiletype);
    }
};

}

#endif //LIBTRELLIS_DATABASE_HPP
