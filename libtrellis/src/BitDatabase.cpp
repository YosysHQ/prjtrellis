#include "BitDatabase.hpp"
#include "CRAM.hpp"
#include "TileConfig.hpp"

#include <algorithm>
#include <fstream>
#include <boost/thread/shared_lock_guard.hpp>
#include <boost/thread/lock_guard.hpp>
#include <boost/range/algorithm/copy.hpp>
#include <boost/range/adaptors.hpp>


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
    return all_of(bits.begin(), bits.end(), [tile](const ConfigBit &b) {
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

void BitGroup::add_coverage(Trellis::BitSet &known_bits) const {
    copy_if(bits.begin(), bits.end(), inserter(known_bits, known_bits.end()), [](ConfigBit b) {
        return !b.inv;
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
    return out;
}

istream &operator>>(istream &in, BitGroup &bits) {
    bits.bits.clear();
    while (!skip_check_eol(in)) {
        string s;
        in >> s;
        bits.bits.push_back(cbit_from_str(s));
    }
    return in;
}

boost::optional<string> MuxBits::get_driver(const CRAMView &tile, boost::optional<BitSet &> coverage) const {
    auto drv = find_if(arcs.begin(), arcs.end(), [tile](const ArcData &a) {
        return a.bits.match(tile);
    });
    if (drv == arcs.end()) {
        return boost::optional<string>();
    } else {
        if (coverage)
            drv->bits.add_coverage(*coverage);
        return boost::optional<string>(drv->source);
    }
}

void MuxBits::set_driver(Trellis::CRAMView &tile, const string &driver) const {
    auto drv = find_if(arcs.begin(), arcs.end(), [driver](const ArcData &a) {
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
    out << endl;
    return out;
}

istream &operator>>(istream &in, MuxBits &mux) {
    in >> mux.sink;
    mux.arcs.clear();
    // Read arc source-bits pairs until end of record
    while (!skip_check_eor(in)) {
        ArcData a;
        a.sink = mux.sink;
        in >> a.source >> a.bits;
        mux.arcs.push_back(a);
    }
    return in;
}

boost::optional<vector<bool>>
WordSettingBits::get_value(const CRAMView &tile, boost::optional<BitSet &> coverage) const {
    vector<bool> val;
    transform(bits.begin(), bits.end(), back_inserter(val), [tile, coverage](const BitGroup &b) {
        bool m = b.match(tile);
        if (coverage)
            b.add_coverage(*coverage);
        return m;
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
    out << endl;
    return out;
}

istream &operator>>(istream &in, WordSettingBits &ws) {
    in >> ws.name;
    bool have_default = false;
    if (!skip_check_eol(in)) {
        in >> ws.defval;
        have_default = true;
    }
    ws.bits.clear();
    while (!skip_check_eor(in)) {
        BitGroup bg;
        in >> bg;
        ws.bits.push_back(bg);
    }
    if (!have_default) {
        ws.defval.clear();
        ws.defval.resize(ws.bits.size(), false);
    }
    return in;
}

boost::optional<string> EnumSettingBits::get_value(const CRAMView &tile, boost::optional<BitSet &> coverage) const {
    auto found = find_if(options.begin(), options.end(), [tile](const pair<string, BitGroup> &kv) {
        return kv.second.match(tile);
    });
    if (found == options.end()) {
        return boost::optional<string>();
    } else {
        if (coverage)
            found->second.add_coverage(*coverage);
        if (defval && *defval == found->first) {
            return boost::optional<string>();
        } else {
            return boost::optional<string>(found->first);
        }
    }
}

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
    out << endl;
    return out;
}

istream &operator>>(istream &in, EnumSettingBits &es) {
    in >> es.name;
    if (!skip_check_eol(in)) {
        string s;
        in >> s;
        es.defval = boost::make_optional(s);
    } else {
        es.defval = boost::optional<string>();
    }
    es.options.clear();
    while (!skip_check_eor(in)) {
        string opt;
        BitGroup bg;
        in >> opt >> bg;
        es.options[opt] = bg;
    }
    return in;
}

TileBitDatabase::TileBitDatabase(const string &filename) : filename(filename) {
    load();
}

void TileBitDatabase::config_to_tile_cram(const TileConfig &cfg, CRAMView &tile) const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    for (auto arc : cfg.carcs)
        muxes.at(arc.from).set_driver(tile, arc.to);
    set<string> found_words, found_enums;
    for (auto cw : cfg.cwords) {
        words.at(cw.name).set_value(tile, cw.value);
        found_words.insert(cw.name);
    }
    for (auto ce : cfg.cenums) {
        enums.at(ce.name).set_value(tile, ce.value);
        found_enums.insert(ce.name);
    }
    for (auto unk : cfg.cunknowns) {
        tile.bit(unk.frame, unk.bit) = 1;
    }
    // Apply default values if not overriden in cfg
    for (auto w : words)
        if (found_words.find(w.first) == found_words.end())
            w.second.set_value(tile, w.second.defval);
    for (auto e : enums)
        if (found_enums.find(e.first) == found_enums.end())
            if (e.second.defval)
                e.second.set_value(tile, *e.second.defval);
}

TileConfig TileBitDatabase::tile_cram_to_config(const CRAMView &tile) const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    TileConfig cfg;
    BitSet coverage;
    for (auto mux : muxes) {
        auto sink = mux.second.get_driver(tile, coverage);
        if (sink)
            cfg.carcs.push_back(ConfigArc{mux.first, *sink});
    }
    for (auto cw : words) {
        auto val = cw.second.get_value(tile, coverage);
        if (val)
            cfg.cwords.push_back(ConfigWord{cw.first, *val});
    }
    for (auto ce : enums) {
        auto val = ce.second.get_value(tile, coverage);
        if (val)
            cfg.cenums.push_back(ConfigEnum{ce.first, *val});
    }
    for (int f = 0; f < tile.frames(); f++) {
        for (int b = 0; b < tile.bits(); b++) {
            if (tile.bit(f, b) && (coverage.find(ConfigBit{f, b, false}) == coverage.end())) {
                cfg.cunknowns.push_back(ConfigUnknown{f, b});
            }
        }
    };
    return cfg;
}

void TileBitDatabase::load() {
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    ifstream in(filename);
    if (!in) {
        throw runtime_error("failed to open tilebit database file " + filename);
    }
    muxes.clear();
    words.clear();
    enums.clear();
    while (!skip_check_eof(in)) {
        string token;
        in >> token;
        if (token == ".mux") {
            MuxBits mux;
            in >> mux;
            muxes[mux.sink] = mux;
        } else if (token == ".config") {
            WordSettingBits cw;
            in >> cw;
            words[cw.name] = cw;
        } else if (token == ".config_enum") {
            EnumSettingBits ce;
            in >> ce;
            enums[ce.name] = ce;
        } else {
            throw runtime_error("unexpected token " + token + " while parsing database file " + filename);
        }
    }
}

void TileBitDatabase::save() {
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    ofstream out(filename);
    if (!out) {
        throw runtime_error("failed to open tilebit database file " + filename + " for writing");
    }
    out << "# Routing Mux Bits" << endl;
    for (auto mux : muxes)
        out << mux.second << endl;
    out << endl << "# Non-Routing Configuration" << endl;
    for (auto word : words)
        out << word.second << endl;
    for (auto senum : enums)
        out << senum.second << endl;
}

set<string> TileBitDatabase::get_sinks() const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    set<string> result;
    boost::copy(muxes | boost::adaptors::map_keys, inserter(result, result.end()));
    return result;
}

MuxBits TileBitDatabase::get_mux_data_for_sink(const string &sink) const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    return muxes.at(sink);
}

set<string> TileBitDatabase::get_settings_words() const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    set<string> result;
    boost::copy(words | boost::adaptors::map_keys, inserter(result, result.end()));
    return result;
}

WordSettingBits TileBitDatabase::get_data_for_setword(const string &name) const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    return words.at(name);
}

set<string> TileBitDatabase::get_settings_enums() const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    set<string> result;
    boost::copy(enums | boost::adaptors::map_keys, inserter(result, result.end()));
    return result;
}

EnumSettingBits TileBitDatabase::get_data_for_enum(const string &name) const {
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    return enums.at(name);
}

}
