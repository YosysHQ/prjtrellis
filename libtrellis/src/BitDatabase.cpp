#include "BitDatabase.hpp"
#include "CRAM.hpp"
#include <algorithm>

namespace Trellis {
ConfigBit cbit_from_str(const string &s) {
    size_t idx = 0;
    ConfigBit b;
    if (s[idx] == '!') {
        b.inv = true;
        ++idx;
    } else {
        b.inv = false;
    }
    assert(s[idx] == 'F');
    ++idx;
    size_t b_pos = s.find('B');
    assert(b_pos != string::npos);
    b.frame = stoi(s.substr(idx, b_pos - idx));
    b.bit = stoi(s.substr(b_pos + 1));
    return b;
}

bool BitGroup::match(const CRAMView &tile) const {
    return all_of(bits.begin(), bits.end(), [tile] (const ConfigBit &b) {
       return tile.bit(b.frame, b.bit) != b.inv;
    });
}

void BitGroup::set_group(CRAMView &tile) const {
    for (auto bit : bits)
        tile.bit(bit.frame, bit.bit) = !bit.inv;
}

void BitGroup::clear_group(Trellis::CRAMView &tile) const {
    for (auto bit : bits)
        tile.bit(bit.frame, bit.bit) = bit.inv;
}

ostream &operator<<(ostream &out, const BitGroup &bits) {
    bool first = false;
    for (auto bit : bits.bits) {
        if (!first)
            out << " ";
        out << to_string(bit);
        first = true;
    }
}

boost::optional<string> MuxBits::get_driver(const CRAMView &tile) const {
    auto drv = find_if(arcs.begin(), arcs.end(), [tile] (const ArcData &a) {
        return a.bits.match(tile);
    });
    if (drv == arcs.end())
        return boost::optional<string>();
    else
        return boost::optional<string>(drv->source);
}

void MuxBits::set_driver(Trellis::CRAMView &tile, const string &driver) const {
    auto drv = find_if(arcs.begin(), arcs.end(), [driver] (const ArcData &a) {
       return a.source == driver;
    });
    if (drv == arcs.end()) {
        throw runtime_error("sink " + sink + " has no driver named " + driver);
    }
    drv->bits.set_group(tile);
}

ostream &operator<<(ostream &out, const MuxBits &mux) {
    out << ".mux " << mux.sink << endl;
    for (const auto &arc : mux.arcs) {
        out << arc.source << " " << arc.bits << endl;
    }
}

boost::optional<vector<bool>> WordSettingBits::get_value(const CRAMView &tile) const {
    vector<bool> val;
    transform(bits.begin(), bits.end(), back_inserter(val), [tile] (const BitGroup &b) {
       return b.match(tile);
    });
    if (val == defval)
        return boost::optional<vector<bool>>();
    else
        return boost::optional<vector<bool>>(val);
}

void WordSettingBits::set_value(Trellis::CRAMView &tile, const vector<bool> &value) const {
    assert(value.size() == bits.size());
    for (size_t i = 0; i < bits.size(); i++) {
        if (value.at(i))
            bits.at(i).set_group(tile);
        else
            bits.at(i).clear_group(tile);
    }
}

ostream &operator<<(ostream &out, const WordSettingBits &ws) {
    out << ".config " << ws.name << " " << to_string(ws.defval) << endl;
    for (const auto &bit : ws.bits) {
        out << bit << endl;
    }
}

boost::optional<string> EnumSettingBits::get_value(const CRAMView &tile) const {
    auto found = find_if(options.begin(), options.end(), [tile](const pair<string, BitGroup> &kv) {
        return kv.second.match(tile);
    });
    if (found == options.end()) {
        return boost::optional<string>();
    } else if (defval && *defval == found->first) {
        return boost::optional<string>();
    } else {
        return boost::optional<string>(found->first);
    }
};

void EnumSettingBits::set_value(Trellis::CRAMView &tile, const string &value) const {
    auto grp = options.at(value);
    grp.set_group(tile);
}

ostream &operator<<(ostream &out, const EnumSettingBits &es) {
    out << ".config_enum " << es.name;
    if (es.defval)
        out << " " << *(es.defval);
    out << endl;
    for (const auto &opt : es.options) {
        out << opt.first << " " << opt.second << endl;
    }
}

}
