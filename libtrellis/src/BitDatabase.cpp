#include "BitDatabase.hpp"
#include "CRAM.hpp"
#include "TileConfig.hpp"
#include "Tile.hpp"
#include "RoutingGraph.hpp"

#include <algorithm>
#include <fstream>
#include <boost/thread/shared_lock_guard.hpp>
#include <boost/thread/lock_guard.hpp>
#include <boost/range/algorithm/copy.hpp>
#include <boost/range/adaptors.hpp>


namespace Trellis {

ConfigBit cbit_from_str(const string &s)
{
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

BitGroup::BitGroup()
{}

BitGroup::BitGroup(const CRAMDelta &delta)
{
    for (const auto &bit: delta) {
        if (bit.delta != 0)
            bits.insert(ConfigBit{bit.frame, bit.bit, (bit.delta < 0)});
    }
}


bool BitGroup::match(const CRAMView &tile) const
{
    return all_of(bits.begin(), bits.end(), [tile](const ConfigBit &b) {
        return tile.bit(b.frame, b.bit) != b.inv;
    });
}

void BitGroup::set_group(CRAMView &tile) const
{
    for (auto bit : bits)
        tile.bit(bit.frame, bit.bit) = !bit.inv;
}

void BitGroup::clear_group(Trellis::CRAMView &tile) const
{
    for (auto bit : bits)
        tile.bit(bit.frame, bit.bit) = bit.inv;
}

void BitGroup::add_coverage(Trellis::BitSet &known_bits, bool value) const
{
    for (const auto &b : bits) {
        if (b.inv != value)
            known_bits.insert(ConfigBit{b.frame, b.bit});
    }
}

ostream &operator<<(ostream &out, const BitGroup &bits)
{
    bool first = true;
    if (bits.bits.empty()) {
        out << "-";
    } else {
        for (auto bit : bits.bits) {
            if (!first)
                out << " ";
            out << to_string(bit);
            first = false;
        }
    }
    return out;
}

istream &operator>>(istream &in, BitGroup &bits)
{
    bits.bits.clear();
    while (!skip_check_eol(in)) {
        string s;
        in >> s;
        if (s == "-")
            break;
        bits.bits.insert(cbit_from_str(s));
    }
    return in;
}

vector<string> MuxBits::get_sources() const
{
    vector<string> result;
    boost::copy(arcs | boost::adaptors::map_keys, back_inserter(result));
    return result;
}

boost::optional<string> MuxBits::get_driver(const CRAMView &tile, boost::optional<BitSet &> coverage) const
{
    boost::optional<const ArcData &> bestmatch;
    size_t bestbits = 0;
    for (const auto &arc : arcs) {
        if (arc.second.bits.match(tile) && arc.second.bits.bits.size() >= bestbits) {
            bestmatch = arc.second;
            bestbits = arc.second.bits.bits.size();
        }
    }
    if (!bestmatch) {
        return boost::optional<string>();
    } else {
        if (coverage)
            bestmatch->bits.add_coverage(*coverage);
        return boost::optional<string>(bestmatch->source);
    }
}

void MuxBits::set_driver(Trellis::CRAMView &tile, const string &driver) const
{
    auto drv = arcs.find(driver);
    if (drv == arcs.end()) {
        throw runtime_error("sink " + sink + " has no driver named " + driver);
    }
    drv->second.bits.set_group(tile);
}

ostream &operator<<(ostream &out, const MuxBits &mux)
{
    out << ".mux " << mux.sink << endl;
    for (const auto &arc : mux.arcs) {
        out << arc.first << " " << arc.second.bits << endl;
    }
    return out;
}

istream &operator>>(istream &in, MuxBits &mux)
{
    in >> mux.sink;
    mux.arcs.clear();
    // Read arc source-bits pairs until end of record
    while (!skip_check_eor(in)) {
        ArcData a;
        a.sink = mux.sink;
        in >> a.source >> a.bits;
        mux.arcs[a.source] = a;
    }
    return in;
}

boost::optional<vector<bool>>
WordSettingBits::get_value(const CRAMView &tile, boost::optional<BitSet &> coverage) const
{
    vector<bool> val;
    transform(bits.begin(), bits.end(), back_inserter(val), [tile, coverage](const BitGroup &b) {
        bool m = b.match(tile);
        if (coverage)
            b.add_coverage(*coverage, m);
        return m;
    });
    if (val == defval)
        return boost::optional<vector<bool>>();
    else
        return boost::optional<vector<bool>>(val);
}

void WordSettingBits::set_value(Trellis::CRAMView &tile, const vector<bool> &value) const
{
    assert(value.size() == bits.size());
    for (size_t i = 0; i < bits.size(); i++) {
        if (value.at(i))
            bits.at(i).set_group(tile);
        else
            bits.at(i).clear_group(tile);
    }
}

ostream &operator<<(ostream &out, const WordSettingBits &ws)
{
    out << ".config " << ws.name << " " << to_string(ws.defval) << endl;
    for (const auto &bit : ws.bits) {
        out << bit << endl;
    }
    return out;
}

istream &operator>>(istream &in, WordSettingBits &ws)
{
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

void EnumSettingBits::set_defval(string val)
{
    defval = val;
}


string EnumSettingBits::get_defval() const
{
    if (defval)
        return *defval;
    else
        return "";
}

vector<string> EnumSettingBits::get_options() const
{
    vector<string> result;
    boost::copy(options | boost::adaptors::map_keys, back_inserter(result));
    return result;
}

boost::optional<string> EnumSettingBits::get_value(const CRAMView &tile, boost::optional<BitSet &> coverage) const
{
    boost::optional<const pair<const string, BitGroup> &> bestmatch;
    size_t bestbits = 0;
    for (const auto &opt : options) {
        if (opt.second.match(tile) && opt.second.bits.size() >= bestbits) {
            bestmatch = opt;
            bestbits = opt.second.bits.size();
        }
    }
    if (!bestmatch) {
        if (defval) {
            return boost::optional<string>("_NONE_");
        } else {
            return boost::optional<string>();
        }
    } else {
        if (coverage)
            bestmatch->second.add_coverage(*coverage);
        if (defval && (options.at(*defval) == bestmatch->second)) {
            return boost::optional<string>();
        } else {
            return boost::optional<string>(bestmatch->first);
        }
    }
}

void EnumSettingBits::set_value(Trellis::CRAMView &tile, const string &value) const
{
    if (value != "_NONE_") {
        if(options.find(value) != options.end()) {
            auto grp = options.at(value);
            grp.set_group(tile);
	}
	else {
	    cerr << "EnumSettingBits::set_value: cannot set " << value  << endl;
	    cerr << "In Options: " << endl;
	    for(auto it = options.begin(); it != options.end(); ++it){
	      cerr << it->first << " -> " << it->second << endl;
	    }

	    exit(1);
	}
    }
}

ostream &operator<<(ostream &out, const EnumSettingBits &es)
{
    out << ".config_enum " << es.name;
    if (es.defval)
        out << " " << *(es.defval);
    out << endl;
    for (const auto &opt : es.options) {
        out << opt.first << " " << opt.second << endl;
    }
    return out;
}

istream &operator>>(istream &in, EnumSettingBits &es)
{
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

ostream &operator<<(ostream &out, const FixedConnection &es)
{
    out << ".fixed_conn " << es.sink << " " << es.source << endl;
    return out;
}

istream &operator>>(istream &in, FixedConnection &es)
{
    in >> es.sink >> es.source;
    return in;
}


TileBitDatabase::TileBitDatabase(const string &filename) : filename(filename)
{
    load();
}

void TileBitDatabase::config_to_tile_cram(const TileConfig &cfg, CRAMView &tile, bool is_tilegroup, set<string> *tg_matches) const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    for (auto arc : cfg.carcs)
        muxes.at(arc.sink).set_driver(tile, arc.source);
    set<string> found_words, found_enums;
    // Make sure "base" enums like IO type are applied first, other settings may overlay onto them later
    const string base_prefix = "BASE_";
    for (auto ce : cfg.cenums) {
        if (ce.name.substr(0, base_prefix.length()) == base_prefix) {
            if (is_tilegroup && !enums.count(ce.name))
                continue;
            if (is_tilegroup && !enums.at(ce.name).options.count(ce.value))
                continue;
            if (tg_matches)
                tg_matches->insert(ce.name);
            enums.at(ce.name).set_value(tile, ce.value);
            found_enums.insert(ce.name);
        }
    }
    for (auto cw : cfg.cwords) {
        if (is_tilegroup && !words.count(cw.name))
            continue;
        if (tg_matches)
            tg_matches->insert(cw.name);
        words.at(cw.name).set_value(tile, cw.value);
        found_words.insert(cw.name);
    }
    for (auto ce : cfg.cenums) {
        if (ce.name.substr(0, base_prefix.length()) != base_prefix) {
            if (is_tilegroup && !enums.count(ce.name))
                continue;
            if (is_tilegroup && !enums.at(ce.name).options.count(ce.value))
                continue;
            if (tg_matches)
                tg_matches->insert(ce.name);
            enums.at(ce.name).set_value(tile, ce.value);
            found_enums.insert(ce.name);
        }
    }
    for (auto unk : cfg.cunknowns) {
        tile.bit(unk.frame, unk.bit) = 1;
    }
    // Apply default values if not overriden in cfg
    if (!is_tilegroup) {
        for (auto w : words)
            if (found_words.find(w.first) == found_words.end())
                w.second.set_value(tile, w.second.defval);
        for (auto e : enums)
            if (found_enums.find(e.first) == found_enums.end())
                if (e.second.defval)
                    e.second.set_value(tile, *e.second.defval);
    }

}

TileConfig TileBitDatabase::tile_cram_to_config(const CRAMView &tile) const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    TileConfig cfg;
    BitSet coverage;
    for (auto mux : muxes) {
        auto sink = mux.second.get_driver(tile, coverage);
        if (sink && mux.second.arcs.at(*sink).bits.bits.size() > 0)
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
            if (tile.bit(f, b)) {
                if (coverage.find(ConfigBit{f, b, false}) == coverage.end()) {
                    cfg.cunknowns.push_back(ConfigUnknown{f, b});
                } else {
                    cfg.total_known_bits++;
                }
            }
        }
    };
    return cfg;
}

void TileBitDatabase::load()
{
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
        } else if (token == ".fixed_conn") {
            FixedConnection c;
            in >> c;
            fixed_conns[c.sink].insert(c);
        } else {
            throw runtime_error("unexpected token " + token + " while parsing database file " + filename);
        }
    }
}

void TileBitDatabase::save()
{
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
    out << endl << "# Fixed Connections" << endl;
    for (auto conns : fixed_conns)
        for (auto conn2 : conns.second)
            out << conn2 << endl;
    dirty = false;
}

vector<string> TileBitDatabase::get_sinks() const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    vector<string> result;
    boost::copy(muxes | boost::adaptors::map_keys, back_inserter(result));
    return result;
}

MuxBits TileBitDatabase::get_mux_data_for_sink(const string &sink) const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    return muxes.at(sink);
}

vector<string> TileBitDatabase::get_settings_words() const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    vector<string> result;
    boost::copy(words | boost::adaptors::map_keys, back_inserter(result));
    return result;
}

WordSettingBits TileBitDatabase::get_data_for_setword(const string &name) const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    return words.at(name);
}

vector<string> TileBitDatabase::get_settings_enums() const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    vector<string> result;
    boost::copy(enums | boost::adaptors::map_keys, back_inserter(result));
    return result;
}

EnumSettingBits TileBitDatabase::get_data_for_enum(const string &name) const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    return enums.at(name);
}

vector<FixedConnection> TileBitDatabase::get_fixed_conns() const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    vector<FixedConnection> result;
    for (const auto &csink : fixed_conns) {
        for (const auto &conn : csink.second) {
            result.push_back(conn);
        }
    }
    return result;
}

vector<pair<string, bool>> TileBitDatabase::get_downhill_wires(const string &wire) const
{
    vector<pair<string, bool>> dhwires;
    for (const auto &mux : muxes) {
        for (const auto &arc : mux.second.arcs) {
            if (arc.second.source == wire)
                dhwires.push_back(make_pair(arc.second.sink, true));
        }
    }
    for (const auto &csink : fixed_conns) {
        for (const auto &conn : csink.second) {
            if (conn.source == wire)
                dhwires.push_back(make_pair(conn.sink, false));
        }
    }
    return dhwires;
}

void TileBitDatabase::add_routing(const TileInfo &tile, RoutingGraph &graph) const
{
    boost::shared_lock_guard<boost::shared_mutex> guard(db_mutex);
    int row, col;
    tie(row, col) = tile.get_row_col();
    Location loc(col, row);
    for (const auto &mux : muxes) {
        RoutingId sink = graph.globalise_net(row, col, mux.second.sink);
        if (sink == RoutingId())
            continue;
        for (const auto &arc : mux.second.arcs) {
            RoutingId src = graph.globalise_net(row, col, arc.second.source);
            if (src == RoutingId())
                continue;
            RoutingArc rarc;
            rarc.id = graph.ident(arc.second.source + "->" + arc.second.sink);
            rarc.source = src;
            rarc.sink = sink;
            rarc.tiletype = graph.ident(tile.type);
            rarc.configurable = true;
            graph.add_arc(loc, rarc);
        }
    }

    for (const auto &fcs : fixed_conns) {
        for (const auto &fc : fcs.second) {
            RoutingId sink = graph.globalise_net(row, col, fc.sink);
            if (sink == RoutingId())
                continue;
            RoutingId src = graph.globalise_net(row, col, fc.source);
            if (src == RoutingId())
                continue;
            RoutingArc rarc;
            rarc.id = graph.ident(fc.source + "=>" + fc.sink);
            rarc.source = src;
            rarc.sink = sink;
            rarc.tiletype = graph.ident(tile.type);
            rarc.configurable = false;
            graph.add_arc(loc, rarc);
        }
    }
}

void TileBitDatabase::add_mux_arc(const ArcData &arc)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    dirty = true;
    if (muxes.find(arc.sink) == muxes.end()) {
        MuxBits mux;
        mux.sink = arc.sink;
        muxes[mux.sink] = mux;
    }
    MuxBits &curr = muxes.at(arc.sink);
    auto found = curr.arcs.find(arc.source);
    if (found == curr.arcs.end()) {
        curr.arcs[arc.source] = arc;
    } else {
        if (found->second.bits == arc.bits) {
            // In DB already, no-op
        } else {
            throw DatabaseConflictError(fmt("database conflict: arc " << arc.source << " -> " << arc.sink <<
                                                                      " already in DB, but config bits " <<
                                                                      arc.bits
                                                                      << " don't match existing DB bits " <<
                                                                      found->second.bits));
        }
    }

}

void TileBitDatabase::add_setting_word(const WordSettingBits &wsb)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    dirty = true;
    if (words.find(wsb.name) != words.end()) {
        WordSettingBits &curr = words.at(wsb.name);
        if (curr.bits.size() != wsb.bits.size()) {
            throw DatabaseConflictError(fmt("word " << curr.name << " already exists in DB, but new size "
                                                    << wsb.bits.size() << " does not match existing size "
                                                    << curr.bits.size()));
        }
        for (size_t i = 0; i < curr.bits.size(); i++) {
            if (!(curr.bits.at(i) == wsb.bits.at(i))) {
                throw DatabaseConflictError(fmt("bit " << wsb.name << "[" << i << "] already in DB, but config bits "
                                                       << wsb.bits.at(i) << " don't match existing DB bits "
                                                       << curr.bits.at(i)));
            }
        }
    } else {
        words[wsb.name] = wsb;
    }
}

void TileBitDatabase::add_setting_enum(const EnumSettingBits &esb)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    dirty = true;
    if (enums.find(esb.name) != enums.end()) {
        EnumSettingBits &curr = enums.at(esb.name);
        for (const auto &opt : esb.options) {
            if (curr.options.find(opt.first) == curr.options.end()) {
                curr.options[opt.first] = opt.second;
            } else {
                if (curr.options.at(opt.first) == opt.second) {
                    // No-op
                } else {
                    throw DatabaseConflictError(
                            fmt("option " << opt.first << " of " << esb.name << " already in DB, but config bits "
                                          << opt.second << " don't match existing DB bits "
                                          << curr.options.at(opt.first)));
                }
            }
        }
    }
    enums[esb.name] = esb;
}

void TileBitDatabase::add_fixed_conn(const Trellis::FixedConnection &conn)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    fixed_conns[conn.sink].insert(conn);
    dirty = true;
}

TileBitDatabase::TileBitDatabase(const TileBitDatabase &other)
{
    UNUSED(other);
    assert(false);
    terminate();
}

void TileBitDatabase::remove_fixed_sink(const string &sink)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    fixed_conns.erase(sink);
}

void TileBitDatabase::remove_setting_enum(const string &enum_name)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    enums.erase(enum_name);
}

void TileBitDatabase::remove_setting_word(const string &word_name)
{
    boost::lock_guard<boost::shared_mutex> guard(db_mutex);
    words.erase(word_name);
}

DatabaseConflictError::DatabaseConflictError(const string &desc) : runtime_error(desc)
{}

TileBitDatabase::~TileBitDatabase()
{
    if (dirty)
        save();
}

}
