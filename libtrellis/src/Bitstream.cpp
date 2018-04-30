#include "Bitstream.hpp"
#include "Chip.hpp"
#include <sstream>
#include <cstring>
#include <algorithm>
#include <iterator>

namespace Trellis {

static const uint16_t CRC16_POLY = 0x8005;
static const uint16_t CRC16_INIT = 0x0000;
// The BitstreamReader class stores state (including CRC16) whilst reading
// the bitstream
class BitstreamReader {
public:
    BitstreamReader(const vector<uint8_t> &data) : data(data), iter(data.begin()) {};

    const vector<uint8_t> &data;
    vector<uint8_t>::const_iterator iter;

    uint16_t crc16 = CRC16_INIT;

    // Add a single byte to the running CRC16 accumulator
    void update_crc16(uint8_t val) {
        int bit_flag;
        for (int i = 7; i >= 0; i--) {
            bit_flag = crc16 >> 15;

            /* Get next bit: */
            crc16 <<= 1;
            crc16 |= (val >> i) & 1; // item a) work from the least significant bits

            /* Cycle check: */
            if (bit_flag)
                crc16 ^= CRC16_POLY;
        }

    }

    // Return a single byte and update CRC
    inline uint8_t get_byte() {
        uint8_t val = *(iter++);
        update_crc16(val);
        return val;
    }

    // Copy multiple bytes into an OutputIterator and update CRC
    template<typename T>
    void get_bytes(T out, size_t count) {
        for (size_t i = 0; i < count; i++) {
            *out = get_byte();
            ++out;
        }
    }

    // Skip over bytes while updating CRC
    void skip_bytes(size_t count) {
        for (size_t i = 0; i < count; i++) get_byte();
    }

    bool find_preamble(const vector<uint8_t> &preamble) {
        auto found = search(iter, data.end(), preamble.begin(), preamble.end());
        if (found == data.end())
            return false;
        iter = found + preamble.size();
        return true;
    }

    uint16_t finalise_crc16() {
        // item b) "push out" the last 16 bits
        int i, bit_flag;
        for (i = 0; i < 16; ++i) {
            bit_flag = crc16 >> 15;
            crc16 <<= 1;
            if(bit_flag)
                crc16 ^= CRC16_POLY;
        }

        return crc16;
    }

    void reset_crc16() {
        crc16 = CRC16_INIT;
    }

    void check_crc16() {
        uint8_t crc_bytes[2];
        uint16_t actual_crc = finalise_crc16();
        get_bytes(crc_bytes, 2);
        uint16_t exp_crc = (crc_bytes[0] << 8) | crc_bytes[1];
        if (actual_crc != exp_crc) {
            ostringstream err;
            err << "crc fail, calculated 0x" << hex << actual_crc << " but expecting 0x" << exp_crc;
            throw BitstreamParseError(err.str(), distance(data.begin(), iter));
        }
    }

    bool is_end() {
        return (iter >= data.end());
    }
};

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

Chip Bitstream::deserialise_chip() {
    // TODO
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
