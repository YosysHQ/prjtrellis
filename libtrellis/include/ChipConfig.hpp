#ifndef CHIPCONFIG_H
#define CHIPCONFIG_H

#include "TileConfig.hpp"
#include <map>
#include <vector>
#include <string>

using namespace std;

namespace Trellis {

class Chip;

// This represents the configuration of a chip at a high level
class ChipConfig
{
    string chip_name;
    vector<string> metadata;
    map<string, TileConfig> tiles;
    string to_string() const;
    static ChipConfig from_string(const string &config);
    Chip to_chip() const;
    static ChipConfig from_chip(const Chip &chip);
};

}

#endif
