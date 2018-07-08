#include "TileConfig.hpp"
#include "Util.hpp"
#include "BitDatabase.hpp"
#include <algorithm>
#include <sstream>
using namespace std;

namespace Trellis {
ostream &operator<<(ostream &out, const ConfigArc &arc) {
    out << "arc: " << arc.sink << " " << arc.source << endl;
    return out;
}

istream &operator>>(istream &in, ConfigArc &arc) {
    in >> arc.sink;
    in >> arc.source;
    return in;
}

ostream &operator<<(ostream &out, const ConfigWord &cw) {
    out << "word: " << cw.name << " " << to_string(cw.value) << endl;
    return out;
}

istream &operator>>(istream &in, ConfigWord &cw) {
    in >> cw.name;
    in >> cw.value;
    return in;
}

ostream &operator<<(ostream &out, const ConfigEnum &cw) {
    out << "enum: " << cw.name << " " << cw.value << endl;
    return out;
}

istream &operator>>(istream &in, ConfigEnum &ce) {
    in >> ce.name;
    in >> ce.value;
    return in;
}

ostream &operator<<(ostream &out, const ConfigUnknown &cu) {
    out << "unknown: " << to_string(ConfigBit{cu.frame, cu.bit, false}) << endl;
    return out;
}

istream &operator>>(istream &in, ConfigUnknown &cu) {
    string s;
    in >> s;
    ConfigBit c = cbit_from_str(s);
    cu.frame = c.frame;
    cu.bit = c.bit;
    assert(!c.inv);
    return in;
}

ostream &operator<<(ostream &out, const TileConfig &tc) {
    for (const auto &arc : tc.carcs)
        out << arc;
    for (const auto &cword : tc.cwords)
        out << cword;
    for (const auto &cenum : tc.cenums)
        out << cenum;
    for (const auto &cunk : tc.cunknowns)
        out << cunk;
    return out;
}

istream &operator>>(istream &in, TileConfig &tc) {
    tc.carcs.clear();
    tc.cwords.clear();
    tc.cenums.clear();
    while (!skip_check_eor(in)) {
        string type;
        in >> type;
        if (type == "arc:") {
            ConfigArc a;
            in >> a;
            tc.carcs.push_back(a);
        } else if (type == "word:") {
            ConfigWord w;
            in >> w;
            tc.cwords.push_back(w);
        } else if (type == "enum:") {
            ConfigEnum e;
            in >> e;
            tc.cenums.push_back(e);
        } else if (type == "unknown:") {
            ConfigUnknown u;
            in >> u;
            tc.cunknowns.push_back(u);
        } else {
            throw runtime_error("unexpected token " + type + " while reading config text");
        }
    }
    return in;
}

void TileConfig::add_arc(const string &sink, const string &source) {
    carcs.push_back({sink, source});
}

void TileConfig::add_word(const string &name, const vector<bool> &value) {
    cwords.push_back({name, value});
}

void TileConfig::add_enum(const string &name, const string &value) {
    cenums.push_back({name, value});
}

void TileConfig::add_unknown(int frame, int bit) {
    cunknowns.push_back({frame, bit});
}


string TileConfig::to_string() const {
    stringstream ss;
    ss << *this;
    return ss.str();
}

TileConfig TileConfig::from_string(const string &str) {
    stringstream ss(str);
    TileConfig tc;
    ss >> tc;
    return tc;
}

bool TileConfig::empty() const {
    return carcs.empty() && cwords.empty() && cenums.empty() && cunknowns.empty();
}

}
