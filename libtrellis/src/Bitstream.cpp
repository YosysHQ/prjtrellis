#include "Bitstream.hpp"
#include <sstream>
#include <cstring>
#include <algorithm>
#include <iterator>

namespace Trellis {
Bitstream::Bitstream(const vector<uint8_t> &data, const vector<string> &metadata) : data(data), metadata(metadata) {}

Bitstream Bitstream::read_bit(istream &in) {
    vector<uint8_t> bytes;
    vector<string> meta;
    auto hdr1 = uint8_t(in.get());
    auto hdr2 = uint8_t(in.get());
    if (hdr1 != 0xFF || hdr2 != 0x00) {
        throw BitstreamParseError("Lattice .BIT files must start with 0xFF, 0x00", 0);
    }
    std::string temp;
    uint8_t c;
    while ((c = uint8_t(in.get())) != 0xFF) {
        if (in.eof())
            throw BitstreamParseError("Encountered end of file before start of bitstream data");
        if (c == '\0') {
            meta.push_back(temp);
            temp = "";
        } else {
            temp += char(c);
        }
    }
    copy(istream_iterator<uint8_t>(in), istream_iterator<uint8_t>(),
         back_inserter(bytes));
    return Bitstream(bytes, meta);
}

void Bitstream::write_bit(ostream &out) {
    // Write metadata header
    out.put(0xFF);
    out.put(0x00);
    for (auto str : metadata) {
        out << str;
        out.put(0x00);
    }
    out.put(0xFF);
    // Dump raw bitstream
    write_bin(out);
}

void Bitstream::write_bin(ostream &out) {
    copy(data.begin(), data.end(), ostream_iterator<uint8_t>(out));
}

BitstreamParseError::BitstreamParseError(const string &desc) : desc(desc), offset(-1), runtime_error(desc.c_str()) {};

BitstreamParseError::BitstreamParseError(const string &desc, size_t offset) : desc(desc), offset(int(offset)),
                                                                              runtime_error(desc.c_str()) {};

const char *BitstreamParseError::what() const noexcept {
    ostringstream ss;
    ss << "Bitstream Parse Error: ";
    ss << desc;
    if (offset != -1)
        ss << "[at 0x" << hex << offset << "]";
    return strdup(ss.str().c_str());
}

}
