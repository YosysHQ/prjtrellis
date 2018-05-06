#ifndef LIBTRELLIS_BITDATABASE_HPP
#define LIBTRELLIS_BITDATABASE_HPP

#include <vector>
#include <map>
#include <string>
#include <cstdint>
#include <boost/optional.hpp>
#include "Util.hpp"

using namespace std;
namespace Trellis {
/*
The BitDatabase keeps track of what each bit in a tile does. Unlike other databases, this database is mutable from
 within libtrellis, for use during fuzzing.
 */

// A single configuration bit, given by its offset inside the tile,
// and whether or not it is inverted
struct ConfigBit {
    int frame;
    int bit;
    bool inv = false;
};

// Write a configuration bit to string
inline string to_string(ConfigBit b) {
    ostringstream ss;
    if (b.inv) ss << "!";
    ss << "F" << b.frame;
    ss << "B" << b.bit;
}

// Read a configuration bit from a string
ConfigBit cbit_from_str(const string &s);

class CRAMView;

// A BitGroup is a list of configuration bits that correspond to a given setting
struct BitGroup {
    vector<ConfigBit> bits;

    // Return true if the BitGroup is set in a tile
    bool match(const CRAMView &tile) const;
};

ostream &operator<<(ostream &out, const BitGroup &bits);

// An arc is a configurable connection between two nodes, defined within a mux
struct Arc {
    string source;
    string sink;
    BitGroup bits;
};

// A mux specifies all the possible source node arcs driving a sink node
struct Mux {
    string sink;
    vector<Arc> arcs;

    // Work out which connection inside the mux, if any, is made inside a tile
    boost::optional<string> get_driver(const CRAMView &tile) const;
};

ostream &operator<<(ostream &out, const Mux &mux);


// There are three types of non-routing config setting in the database
// word  : a multibit setting, such as LUT initialisation
// simple: a single on/off setting, a special case of the above
// enum  : a setting with several different textual values, such as an IO type

struct WordSetting {
    string name;
    vector<BitGroup> bits;
    vector<bool> defval;

    boost::optional<vector<bool>> get_value(const CRAMView &tile) const;
};

ostream &operator<<(ostream &out, const WordSetting &ws);

struct EnumSetting {
    string name;
    map<string, BitGroup> options;
    boost::optional<string> defval;
    boost::optional<string> get_value(const CRAMView &tile) const;
};

ostream &operator<<(ostream &out, const EnumSetting &es);

}

#endif //LIBTRELLIS_BITDATABASE_HPP
