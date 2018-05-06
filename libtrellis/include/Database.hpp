#ifndef LIBTRELLIS_DATABASE_HPP
#define LIBTRELLIS_DATABASE_HPP

#include <string>
#include <cstdint>
#include <vector>

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
    string family;
    string device;
    string tiletype;
};

// Search the device list by part name
DeviceLocator find_device_by_name(string name);

// Search the device list by ID
DeviceLocator find_device_by_idcode(uint32_t idcode);

struct ChipInfo;

// Obtain basic information about a device
ChipInfo get_chip_info(const DeviceLocator &part);

// Obtain the tilegrid for a part
struct TileInfo;

vector<TileInfo> get_device_tilegrid(const DeviceLocator &part);
};


#endif //LIBTRELLIS_DATABASE_HPP
