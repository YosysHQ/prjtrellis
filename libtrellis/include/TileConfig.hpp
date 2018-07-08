#ifndef LIBTRELLIS_TILECONFIG_HPP
#define LIBTRELLIS_TILECONFIG_HPP

#include <string>
#include <cstdint>
#include <vector>
#include <map>
#include <iostream>

using namespace std;

namespace Trellis {
// This represents configuration at FASM level, in terms of routing arcs and non-routing configuration settings -
// either words or enums.

// A connection in a tile
struct ConfigArc {
    string sink;
    string source;
    inline bool operator==(const ConfigArc &other) const {
        return other.source == source && other.sink == sink;
    }
};

ostream &operator<<(ostream &out, const ConfigArc &arc);

istream &operator>>(istream &in, ConfigArc &arc);

// A configuration setting in a tile that takes one or more bits (such as LUT init)
struct ConfigWord {
    string name;
    vector<bool> value;
    inline bool operator==(const ConfigWord &other) const {
        return other.name == name && other.value == value;
    }
};

ostream &operator<<(ostream &out, const ConfigWord &cw);

istream &operator>>(istream &in, ConfigWord &cw);

// A configuration setting in a tile that takes an enumeration value (such as IO type)
struct ConfigEnum {
    string name;
    string value;
    inline bool operator==(const ConfigEnum &other) const {
        return other.name == name && other.value == value;
    }
};

ostream &operator<<(ostream &out, const ConfigEnum &ce);

istream &operator>>(istream &in, ConfigEnum &ce);

// An unknown bit, specified by position only
struct ConfigUnknown {
    int frame, bit;
    inline bool operator==(const ConfigUnknown &other) const {
        return other.frame == frame && other.bit == bit;
    }
};

ostream &operator<<(ostream &out, const ConfigUnknown &tc);

istream &operator>>(istream &in, ConfigUnknown &ce);

struct TileConfig {
    vector<ConfigArc> carcs;
    vector<ConfigWord> cwords;
    vector<ConfigEnum> cenums;
    vector<ConfigUnknown> cunknowns;
    int total_known_bits = 0;

    void add_arc(const string &sink, const string &source);
    void add_word(const string &name, const vector<bool> &value);
    void add_enum(const string &name, const string &value);
    void add_unknown(int frame, int bit);

    string to_string() const;
    static TileConfig from_string(const string &str);

    bool empty() const;
};

ostream &operator<<(ostream &out, const TileConfig &tc);

istream &operator>>(istream &in, TileConfig &ce);

}

#endif //LIBTRELLIS_TILECONFIG_HPP
