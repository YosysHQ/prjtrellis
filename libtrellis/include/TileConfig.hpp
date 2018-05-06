#ifndef LIBTRELLIS_TILECONFIG_HPP
#define LIBTRELLIS_TILECONFIG_HPP

#include <string>
#include <cstdint>
#include <vector>
#include <map>

using namespace std;

namespace Trellis {
// This represents configuration at FASM level, in terms of routing arcs and non-routing configuration settings -
// either words or enums.

// A connection in a tile
struct ConfigArc {
    string from;
    string to;
};

ostream &operator<<(ostream &out, const ConfigArc &arc);

istream &operator>>(istream &in, ConfigArc &arc);

// A configuration setting in a tile that takes one or more bits (such as LUT init)
struct ConfigWord {
    string name;
    vector<bool> value;
};

ostream &operator<<(ostream &out, const ConfigWord &cw);

istream &operator>>(istream &in, ConfigWord &cw);

// A configuration setting in a tile that takes an enumeration value (such as IO type)
struct ConfigEnum {
    string name;
    string value;
};

ostream &operator<<(ostream &out, const ConfigEnum &ce);

istream &operator>>(istream &in, ConfigEnum &ce);

struct TileConfig {
    vector<ConfigArc> carcs;
    vector<ConfigWord> cwords;
    vector<ConfigEnum> cenums;
};

}

#endif //LIBTRELLIS_TILECONFIG_HPP
