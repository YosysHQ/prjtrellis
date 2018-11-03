#ifndef LIBTRELLIS_BITDATABASE_HPP
#define LIBTRELLIS_BITDATABASE_HPP

#include <vector>
#include <map>
#include <string>
#include <cstdint>
#include <boost/optional.hpp>
#include <mutex>
#include <boost/thread/shared_mutex.hpp>
#include <atomic>
#include <set>
#include <unordered_set>
#include "Util.hpp"

#ifdef FUZZ_SAFETY_CHECK

#include <boost/interprocess/sync/file_lock.hpp>

#endif

using namespace std;
namespace Trellis {
/*
The BitDatabase keeps track of what each bit in a tile does. Unlike other databases, this database is mutable from
 within libtrellis, for use during fuzzing.
 */

// A single configuration bit, given by its offset inside the tile,
// and whether or not it is inverted
struct ConfigBit
{
    int frame;
    int bit;
    bool inv = false;

    inline bool operator==(const ConfigBit &other) const
    {
        return (frame == other.frame) && (bit == other.bit) && (inv == other.inv);
    }
};

inline bool operator<(const ConfigBit &a, const ConfigBit &b)
{
    if (a.frame < b.frame) {
        return true;
    } else if (a.frame > b.frame) {
        return false;
    } else {
        if (a.bit < b.bit) {
            return true;
        } else if (a.bit > b.bit) {
            return false;
        } else {
            return a.inv < b.inv;
        }
    }
}
}

namespace std {
// Hash function for ConfigBit
template<>
struct hash<Trellis::ConfigBit>
{
public:
    inline size_t operator()(const Trellis::ConfigBit &bit) const
    {
        hash<int> hash_i_fn;
        hash<bool> hash_b_fn;
        return hash_i_fn(bit.frame) + hash_i_fn(bit.bit) + hash_b_fn(bit.inv);
    }
};
}

namespace Trellis {
typedef unordered_set<ConfigBit> BitSet;

// Write a configuration bit to string
inline string to_string(ConfigBit b)
{
    ostringstream ss;
    if (b.inv) ss << "!";
    ss << "F" << b.frame;
    ss << "B" << b.bit;
    return ss.str();
}

// Read a configuration bit from a string
ConfigBit cbit_from_str(const string &s);

class CRAMView;

struct ChangedBit;
typedef vector<ChangedBit> CRAMDelta;

// A BitGroup is a list of configuration bits that correspond to a given setting
struct BitGroup
{
    // Create an empty BitGroup
    BitGroup();

    // Create a BitGroup from a delta.
    // Delta should be calculated as (with feature) - (without feature)
    explicit BitGroup(const CRAMDelta &delta);

    set<ConfigBit> bits;

    // Return true if the BitGroup is set in a tile
    bool match(const CRAMView &tile) const;

    // Update a coverage set with the bitgroup
    void add_coverage(BitSet &known_bits, bool value = true) const;

    // Set the BitGroup in a tile
    void set_group(CRAMView &tile) const;

    // Clear the BitGroup in a tile
    void clear_group(CRAMView &tile) const;

    inline bool operator==(const BitGroup &other) const
    {
        return bits == other.bits;
    }
};

// Write BitGroup to output
ostream &operator<<(ostream &out, const BitGroup &bits);

// Read a BitGroup from input (until end of line)
istream &operator>>(istream &out, BitGroup &bits);

// An arc is a configurable connection between two nodes, defined within a mux
struct ArcData
{
    string source;
    string sink;
    BitGroup bits;

    inline bool operator==(const ArcData &other) const
    {
        return (source == other.source) && (sink == other.sink) && (bits == other.bits);
    }
};

// A mux specifies all the possible source node arcs driving a sink node
struct MuxBits
{
    string sink;
    map<string, ArcData> arcs;

    // Get a list of sources for the mux
    vector<string> get_sources() const;

    // Work out which connection inside the mux, if any, is made inside a tile
    boost::optional<string>
    get_driver(const CRAMView &tile, boost::optional<BitSet &> coverage = boost::optional<BitSet &>()) const;

    // Set the driver to a given value inside the tile
    void set_driver(CRAMView &tile, const string &driver) const;

    inline bool operator==(const MuxBits &other) const
    {
        return (sink == other.sink) && (arcs == other.arcs);
    }
};

// Write mux database entry to output
ostream &operator<<(ostream &out, const MuxBits &mux);

// Read mux database entry (excluding .mux token) from input
istream &operator>>(istream &in, MuxBits &mux);

// There are three types of non-routing config setting in the database
// word  : a multibit setting, such as LUT initialisation
// simple: a single on/off setting, a special case of the above
// enum  : a setting with several different textual values, such as an IO type

struct WordSettingBits
{
    string name;
    vector<BitGroup> bits;
    vector<bool> defval;

    // Return the word value in a tile, returning empty if equal to the default
    boost::optional<vector<bool>>
    get_value(const CRAMView &tile, boost::optional<BitSet &> coverage = boost::optional<BitSet &>()) const;

    // Set the word value in a tile
    void set_value(CRAMView &tile, const vector<bool> &value) const;

    inline bool operator==(const WordSettingBits &other) const
    {
        return (name == other.name) && (bits == other.bits) && (defval == other.defval);
    }
};

// Write config word setting bits to output
ostream &operator<<(ostream &out, const WordSettingBits &ws);

// Read config word database entry (excluding .config token) from input
istream &operator>>(istream &out, WordSettingBits &ws);

struct EnumSettingBits
{
    string name;
    map<string, BitGroup> options;
    boost::optional<string> defval;

    // Needed for Python
    void set_defval(string val);

    string get_defval() const;

    vector<string> get_options() const;

    // Get the value of the enumeration, returning empty if not set or set to default, if default is non-empty
    boost::optional<string>
    get_value(const CRAMView &tile, boost::optional<BitSet &> coverage = boost::optional<BitSet &>()) const;

    // Set the value of the enumeration in a tile
    void set_value(CRAMView &tile, const string &value) const;

    inline bool operator==(const EnumSettingBits &other) const
    {
        return (name == other.name) && (options == other.options) && (defval == other.defval);
    }
};

// Write config enum bits to output
ostream &operator<<(ostream &out, const EnumSettingBits &es);

// Read config enum bits database entry (excluding .config_enum token) from input
istream &operator>>(istream &out, EnumSettingBits &es);

// A fixed connection inside a tile
struct FixedConnection
{
    string source;
    string sink;

    inline bool operator==(const FixedConnection &other) const
    {
        return (source == other.source) && (sink == other.sink);
    }
};


inline bool operator<(const FixedConnection &a, const FixedConnection &b)
{
    if (a.sink < b.sink) {
        return true;
    } else if (a.sink > b.sink) {
        return false;
    } else {
        return a.source < b.source;
    }
}

// Write fixed connection to output
ostream &operator<<(ostream &out, const FixedConnection &es);

// Read fixed connection from input
istream &operator>>(istream &out, FixedConnection &es);


struct TileConfig;
struct TileLocator;
struct TileInfo;

class RoutingGraph;

class TileBitDatabase
{
public:
    // Access functions

    // Convert TileConfigs to and from actual Tile CRAM
    void config_to_tile_cram(const TileConfig &cfg, CRAMView &tile, bool is_tilegroup = false, set<string> *tg_matches = nullptr) const;

    TileConfig tile_cram_to_config(const CRAMView &tile) const;

    // All these functions are designed to be thread safe during fuzzing and database modification
    // Maybe we should have faster unsafe versions too, as that will be the majority of the use cases?
    vector<string> get_sinks() const;

    MuxBits get_mux_data_for_sink(const string &sink) const;

    vector<string> get_settings_words() const;

    WordSettingBits get_data_for_setword(const string &name) const;

    vector<string> get_settings_enums() const;

    EnumSettingBits get_data_for_enum(const string &name) const;

    vector<FixedConnection> get_fixed_conns() const;
    // TODO: function to get routing graph of tile

    // Get a list of wires downhill in the tile of a given wire
    // Returns pair<wire, configurable>
    vector<pair<string, bool>> get_downhill_wires(const string &wire) const;

    // Add the bit database for a tile to the routing graph
    void add_routing(const TileInfo &tile, RoutingGraph &graph) const;

    // Add relevant items to the database
    void add_mux_arc(const ArcData &arc);

    void add_setting_word(const WordSettingBits &wsb);

    void add_setting_enum(const EnumSettingBits &esb);

    void add_fixed_conn(const FixedConnection &conn);

    void remove_fixed_sink(const string &sink);
    void remove_setting_enum(const string &enum_name);
    void remove_setting_word(const string &word_name);

    // Save the bit database to file
    void save();

    // Function to obtain the singleton BitDatabase for a given tile
    friend shared_ptr<TileBitDatabase> get_tile_bitdata(const TileLocator &tile);

    // This should not be used, but is required for PyTrellis
    TileBitDatabase(const TileBitDatabase &other);

    ~TileBitDatabase();

private:
    explicit TileBitDatabase(const string &filename);

    mutable boost::shared_mutex db_mutex;
    atomic<bool> dirty{false};
    map<string, MuxBits> muxes;
    map<string, WordSettingBits> words;
    map<string, EnumSettingBits> enums;
    map<string, set<FixedConnection>> fixed_conns;
    string filename;

    void load();

#ifdef FUZZ_SAFETY_CHECK
    boost::interprocess::file_lock ip_db_lock;
#endif
};

// Represents a conflict while adding something to the database
class DatabaseConflictError : public runtime_error
{
public:
    explicit DatabaseConflictError(const string &desc);
};

}

#endif //LIBTRELLIS_BITDATABASE_HPP
