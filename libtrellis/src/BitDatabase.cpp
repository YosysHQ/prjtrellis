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

ostream &operator<<(ostream &out, const BitGroup &bits) {
    bool first = false;
    for (auto bit : bits.bits) {
        if (!first)
            out << " ";
        out << to_string(bit);
        first = true;
    }
}

boost::optional<string> Mux::get_driver(const CRAMView &tile) const {
    auto drv = find_if(arcs.begin(), arcs.end(), [tile] (const Arc &a) {
        return a.bits.match(tile);
    });
    if (drv == arcs.end())
        return boost::optional<string>();
    else
        return boost::optional<string>(drv->source);
}

ostream &operator<<(ostream &out, const Mux &mux) {
    out << ".mux " << mux.sink << endl;
    for (const auto &arc : mux.arcs) {
        out << arc.source << " " << arc.bits << endl;
    }
}

boost::optional<vector<bool>> WordSetting::get_value(const CRAMView &tile) const {
    vector<bool> val;
    transform(bits.begin(), bits.end(), back_inserter(val), [tile] (const BitGroup &b) {
       return b.match(tile);
    });
    if (val == defval)
        return boost::optional<vector<bool>>();
    else
        return boost::optional<vector<bool>>(val);
}

ostream &operator<<(ostream &out, const WordSetting &ws) {
    out << ".config " << ws.name << " " << to_string(ws.defval) << endl;
    for (const auto &bit : ws.bits) {
        out << bit << endl;
    }
}

boost::optional<string> EnumSetting::get_value(const CRAMView &tile) const {
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

ostream &operator<<(ostream &out, const EnumSetting &es) {
    out << ".config_enum " << es.name;
    if (es.defval)
        out << " " << *(es.defval);
    out << endl;
    for (const auto &opt : es.options) {
        out << opt.first << " " << opt.second << endl;
    }
}

}
