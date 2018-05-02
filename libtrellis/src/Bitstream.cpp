#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Util.hpp"
#include <sstream>
#include <cstring>
#include <algorithm>
#include <iterator>
#include <iostream>
#include <boost/optional.hpp>
#include <iomanip>
#include <fstream>

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

    // Read a big endian uint32 from the bitstream
    uint32_t get_uint32() {
        uint8_t tmp[4];
        get_bytes(tmp, 4);
        return (tmp[0] << 24UL) | (tmp[1] << 16UL) | (tmp[2] << 8UL) | (tmp[3]);
    }

    // Search for a preamble, setting bitstream position to be after the preamble
    // Returns true on success, false on failure
    bool find_preamble(const vector<uint8_t> &preamble) {
        auto found = search(iter, data.end(), preamble.begin(), preamble.end());
        if (found == data.end())
            return false;
        iter = found + preamble.size();
        return true;
    }

    uint16_t finalise_crc16() {
        // item b) "push out" the last 16 bits
        int i;
        bool bit_flag;
        for (i = 0; i < 16; ++i) {
            bit_flag = bool(crc16 >> 15);
            crc16 <<= 1;
            if (bit_flag)
                crc16 ^= CRC16_POLY;
        }

        return crc16;
    }

    void reset_crc16() {
        crc16 = CRC16_INIT;
    }

    // Get the offset into the bitstream
    size_t get_offset() {
        return size_t(distance(data.begin(), iter));
    }

    // Check the calculated CRC16 against an actual CRC16, expected in the next 2 bytes
    void check_crc16() {
        uint8_t crc_bytes[2];
        uint16_t actual_crc = finalise_crc16();
        get_bytes(crc_bytes, 2);
        uint16_t exp_crc = (crc_bytes[0] << 8) | crc_bytes[1];
        if (actual_crc != exp_crc) {
            ostringstream err;
            err << "crc fail, calculated 0x" << hex << actual_crc << " but expecting 0x" << exp_crc;
            throw BitstreamParseError(err.str(), get_offset());
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

// TODO: replace these macros with something more flexible
#define BITSTREAM_DEBUG(x) if (verbosity >= VerbosityLevel::DEBUG) cerr << "bitstream: " << x << endl
#define BITSTREAM_NOTE(x) if (verbosity >= VerbosityLevel::NOTE) cerr << "bitstream: " << x << endl
#define BITSTREAM_FATAL(x, pos) { ostringstream ss; ss << x; throw BitstreamParseError(ss.str(), pos); }

static const vector<uint8_t> preamble = {0xFF, 0xFF, 0xBD, 0xB3};

Chip Bitstream::deserialise_chip() {
    BitstreamReader rd(data);
    boost::optional<Chip> chip;
    bool found_preamble = rd.find_preamble(preamble);
    if (!found_preamble)
        throw BitstreamParseError("preamble not found in bitstream");
    while (!rd.is_end()) {
        uint8_t cmd = rd.get_byte();
        switch ((BitstreamCommand) cmd) {
            case BitstreamCommand::LSC_RESET_CRC:
                BITSTREAM_DEBUG("reset crc");
                rd.skip_bytes(3);
                rd.reset_crc16();
                break;
            case BitstreamCommand::VERIFY_ID: {
                rd.skip_bytes(3);
                uint32_t id = rd.get_uint32();
                BITSTREAM_NOTE("device ID: 0x" << hex << setw(8) << setfill('0') << id);
                chip = boost::make_optional(Chip(id));
            }
                break;
            case BitstreamCommand::LSC_PROG_CNTRL0: {
                rd.skip_bytes(3);
                uint32_t cfg = rd.get_uint32();
                BITSTREAM_DEBUG("set control reg 0 to 0x" << hex << setw(8) << setfill('0') << cfg);
            }
                break;
            case BitstreamCommand::ISC_PROGRAM_DONE:
                rd.skip_bytes(3);
                BITSTREAM_NOTE("program DONE");
                break;
            case BitstreamCommand::ISC_PROGRAM_SECURITY:
                rd.skip_bytes(3);
                BITSTREAM_NOTE("program SECURITY");
                break;
            case BitstreamCommand::ISC_PROGRAM_USERCODE: {
                bool check_crc = (rd.get_byte() & 0x80) != 0;
                rd.skip_bytes(2);
                uint32_t uc = rd.get_uint32();
                BITSTREAM_NOTE("set USERCODE to 0x" << hex << setw(8) << setfill('0') << uc);
                chip->usercode = uc;
                if (check_crc)
                    rd.check_crc16();
            }
                break;
            case BitstreamCommand::LSC_INIT_ADDRESS: {
                // This is the main bitstream payload
                if (!chip)
                    throw BitstreamParseError("start of bitstream data before chip was identified", rd.get_offset());
                uint8_t params[3];
                rd.get_bytes(params, 3);
                size_t dummy_bytes = (params[0] & 0x0FU);
                size_t frame_count = (params[1] << 8U) | params[2];
                std::cerr << "reading " << std::dec << frame_count << " config frames (with " << std::dec << dummy_bytes
                          << " dummy bytes)" << std::endl;
                size_t bytes_per_frame = (chip->info.bits_per_frame + chip->info.pad_bits_after_frame +
                                          chip->info.pad_bits_before_frame) / 8U;
                unique_ptr<uint8_t[]> frame_bytes = make_unique<uint8_t[]>(bytes_per_frame);
                for (size_t i = 0; i < frame_count; i++) {
                    rd.get_bytes(frame_bytes.get(), bytes_per_frame);
                    for (size_t j = 0; j < chip->info.bits_per_frame; j++) {
                        size_t ofs = j + chip->info.pad_bits_after_frame;
                        chip->cram.bit((chip->info.num_frames - 1) - i, j) = (char) (
                                (frame_bytes[(bytes_per_frame - 1) - (ofs / 8)] >> (ofs % 8)) & 0x01);
                    }
                    rd.check_crc16();
                    rd.skip_bytes(dummy_bytes);
                }
                rd.reset_crc16();
            }
                break;
            case BitstreamCommand::DUMMY:
                break;
            default: BITSTREAM_FATAL("unsupported command 0x" << hex << setw(2) << setfill('0') << cmd,
                                     rd.get_offset());
        }
    }
    if (chip) {
        return *chip;
    } else {
        throw BitstreamParseError("failed to parse bitstream, no valid payload found");
    }
}


void Bitstream::write_bit(ostream &out) {
    // Write metadata header
    out.put(0xFF);
    out.put(0x00);
    for (const auto &str : metadata) {
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

Bitstream Bitstream::read_bit_py(string file) {
    ifstream inf(file);
    if (!inf)
        throw runtime_error("failed to open input file " + file);
    return read_bit(inf);
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