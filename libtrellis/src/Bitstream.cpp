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
#include <array>

namespace Trellis {

static const uint16_t CRC16_POLY = 0x8005;
static const uint16_t CRC16_INIT = 0x0000;

static const vector<pair<std::string, uint8_t>> frequencies =
    {{"2.4", 0x00},
     {"4.8", 0x01},
     {"9.7", 0x20},
     {"19.4", 0x30},
     {"38.8", 0x38},
     {"62.0", 0x3b}};

static const vector<pair<std::string, uint8_t>> spi_modes =
    {{"fast-read", 0x49},
     {"dual-spi", 0x51},
     {"qspi", 0x59}};

static const uint32_t multiboot_flag = 1 << 20;

// The BitstreamReadWriter class stores state (including CRC16) whilst reading
// the bitstream
class BitstreamReadWriter {
public:
    BitstreamReadWriter() : data(), iter(data.begin()) {};

    BitstreamReadWriter(const vector<uint8_t> &data) : data(data), iter(this->data.begin()) {};

    vector<uint8_t> data;
    vector<uint8_t>::iterator iter;

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
        assert(iter < data.end());
        uint8_t val = *(iter++);
        //cerr << hex << setw(2) << int(val) << endl;
        update_crc16(val);
        return val;
    }

    // The command opcode is a byte so this works like get_byte
    // but doesn't update the CRC if it's a dummy, because the docs
    // says that dummy commands don't update the crc
    inline BitstreamCommand get_command_opcode() {
        assert(iter < data.end());
        uint8_t val = *(iter++);
        BitstreamCommand cmd = BitstreamCommand(val);
        if (cmd != BitstreamCommand::DUMMY)
            update_crc16(val);
        return cmd;
    }

    // Write a single byte and update CRC
    inline void write_byte(uint8_t b) {
        data.push_back(b);
        update_crc16(b);
    }

    // Copy multiple bytes into an OutputIterator and update CRC
    template<typename T>
    void get_bytes(T out, size_t count) {
        for (size_t i = 0; i < count; i++) {
            *out = get_byte();
            ++out;
        }
    }

    // Decompress and copy multiple bytes into an OutputIterator and update CRC
    template<typename T>
    void get_compressed_bytes(T out, size_t count, array<uint8_t, 8> compression_dict) {
        // Here we store data already read by read_byte(), it may be more than 1 byte at times!!
        uint16_t read_data = 0;
        size_t remaining_bits = 0;
        bool next_bit;

        uint8_t udata;

        //
        // Every byte can be encoded by on of 4 cases
        // It's a prefix-free code so we can identify each one just by looking at the first bits:
        // 0 -> Byte zero (0000 0000)
        // 100 xxx -> Stored byte in compression_dict, xxx is the index (0-7)
        // 101 xxx -> Byte with a single bit set, xxx is the index of the set bit (0 is lsb, 7 is msb)
        // 11 xxxxxxxx -> Literal byte, xxxxxxxx is the encoded byte
        //
        for (size_t i = 0; i < count; i++) {
            // Make sure we have at least one bit in the buffer
            if (!remaining_bits) {
                read_data = (uint32_t) get_byte();
                remaining_bits = 8;
            }
            next_bit = bool(read_data >> (remaining_bits-1) & 1);
            remaining_bits--;

            // Check the 4 cases leaving the uncompressed byte in udata
            if (next_bit) {
                // Starts with 1, so check next bit/bits
                // For each of the 3 remaining cases we will need at least 5 more bits,
                // so if we have less than that it's ok to read another byte
                if (remaining_bits < 5) {
                    read_data = (read_data << 8) | ((uint32_t) get_byte());
                    remaining_bits += 8;
                }
                next_bit = bool(read_data >> (remaining_bits-1) & 1);
                remaining_bits--;

                if (next_bit) {
                    // 11 xxxx xxxx: Literal byte, just read the next 8 bits & use that
                    // we consumed 10 bits total
                    if (remaining_bits < 8) {
                        read_data = (read_data << 8) | ((uint32_t) get_byte());
                        remaining_bits += 8;
                    }
                    udata = uint8_t((read_data >> (remaining_bits - 8)) & 0xff);
                    remaining_bits -= 8;
                } else {
                    // Starts with 10, it could be a stored literal or a single-bit-set byte
                    // 10 ? xxx: In both cases we need the index xxx, so extract it now
                    // We already have all the bits we need buffered
                    next_bit = bool(read_data >> (remaining_bits-1) & 1);
                    remaining_bits--;
                    size_t idx = (size_t) ((read_data >> (remaining_bits-3)) & 0x7);
                    remaining_bits -= 3;
                    if (next_bit) {
                        // 101 xxx: Stored byte.  Just use xxx as index in the dictionary,
                        // we consumed 6 bits
                        udata = compression_dict[idx];
                    } else {
                        // 100 xxx: Single-bit-set byte, xxx is the index of the set bit
                        // we consumed 6 bits
                        udata = uint8_t(1 << idx);
                    }
                }
            } else {
                // 0: the uncompressed byte is zero
                // we consumed just one bit
                udata = 0;
            }
            *out = udata;
            ++out;
        }
        // if remaining bits > 0 they are just padding bits added to the end so we can ignore them
    }

    // Write multiple bytes from an InputIterator and update CRC
    template<typename T>
    void write_bytes(T in, size_t count) {
        for (size_t i = 0; i < count; i++)
            write_byte(*(in++));
    }

    // Skip over bytes while updating CRC
    void skip_bytes(size_t count) {
        for (size_t i = 0; i < count; i++) get_byte();
    }

    // Insert zeros while updating CRC
    void insert_zeros(size_t count) {
        for (size_t i = 0; i < count; i++) write_byte(0x00);
    }

    // Insert dummy bytes into the bitstream, without updating CRC
    void insert_dummy(size_t count) {
        for (size_t i = 0; i < count; i++)
            data.push_back(0xFF);
    }

    // Read a big endian uint32 from the bitstream
    uint32_t get_uint32() {
        uint8_t tmp[4];
        get_bytes(tmp, 4);
        return (tmp[0] << 24UL) | (tmp[1] << 16UL) | (tmp[2] << 8UL) | (tmp[3]);
    }

    // Write a big endian uint32_t into the bitstream
    void write_uint32(uint32_t val) {
        write_byte(uint8_t((val >> 24UL) & 0xFF));
        write_byte(uint8_t((val >> 16UL) & 0xFF));
        write_byte(uint8_t((val >> 8UL) & 0xFF));
        write_byte(uint8_t(val & 0xFF));
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
        // cerr << hex << int(crc_bytes[0]) << " " << int(crc_bytes[1]) << endl;
        uint16_t exp_crc = (crc_bytes[0] << 8) | crc_bytes[1];
        if (actual_crc != exp_crc) {
            ostringstream err;
            err << "crc fail, calculated 0x" << hex << actual_crc << " but expecting 0x" << exp_crc;
            throw BitstreamParseError(err.str(), get_offset());
        }
        reset_crc16();
    }

    // Insert the calculated CRC16 into the bitstream, and then reset it
    void insert_crc16() {
        uint16_t actual_crc = finalise_crc16();
        write_byte(uint8_t((actual_crc >> 8) & 0xFF));
        write_byte(uint8_t((actual_crc) & 0xFF));
        reset_crc16();
    }

    bool is_end() {
        return (iter >= data.end());
    }

    const vector<uint8_t> &get() {
        return data;
    };
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
    in.seekg(0, in.end);
    size_t length = in.tellg();
    in.seekg(0, in.beg);
    bytes.resize(length);
    in.read(reinterpret_cast<char *>(&(bytes[0])), length);
    return Bitstream(bytes, meta);
}

// TODO: replace these macros with something more flexible
#define BITSTREAM_DEBUG(x) if (verbosity >= VerbosityLevel::DEBUG) cerr << "bitstream: " << x << endl
#define BITSTREAM_NOTE(x) if (verbosity >= VerbosityLevel::NOTE) cerr << "bitstream: " << x << endl
#define BITSTREAM_FATAL(x, pos) { ostringstream ss; ss << x; throw BitstreamParseError(ss.str(), pos); }

static const vector<uint8_t> preamble = {0xFF, 0xFF, 0xBD, 0xB3};

Chip Bitstream::deserialise_chip() {
    return deserialise_chip(boost::none);
}

Chip Bitstream::deserialise_chip(boost::optional<uint32_t> idcode) {
    cerr << "bitstream size: " << data.size() * 8 << " bits" << endl;
    BitstreamReadWriter rd(data);
    boost::optional<Chip> chip;
    bool found_preamble = rd.find_preamble(preamble);
    boost::optional<array<uint8_t, 8>> compression_dict;

    if (!found_preamble)
        throw BitstreamParseError("preamble not found in bitstream");

    uint16_t current_ebr = 0;
    int addr_in_ebr = 0;

    while (!rd.is_end()) {
        BitstreamCommand cmd = rd.get_command_opcode();
        switch (cmd) {
            case BitstreamCommand::LSC_RESET_CRC:
                BITSTREAM_DEBUG("reset crc");
                rd.skip_bytes(3);
                rd.reset_crc16();
                break;
            case BitstreamCommand::VERIFY_ID: {
                rd.skip_bytes(3);
                uint32_t id = rd.get_uint32();
                if (idcode) {
                    BITSTREAM_NOTE("Overriding device ID from 0x" << hex << setw(8) << setfill('0') << id << " to 0x" << *idcode);
                    id = *idcode;
                }

                BITSTREAM_NOTE("device ID: 0x" << hex << setw(8) << setfill('0') << id);
                chip = boost::make_optional(Chip(id));
                chip->metadata = metadata;
            }
                break;
            case BitstreamCommand::LSC_PROG_CNTRL0: {
                rd.skip_bytes(3);
                uint32_t cfg = rd.get_uint32();
                chip->ctrl0 = cfg;
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
            case BitstreamCommand::LSC_WRITE_COMP_DIC: {
                bool check_crc = (rd.get_byte() & 0x80) != 0;
                rd.skip_bytes(2);
                compression_dict = boost::make_optional(array<uint8_t, 8>());
                // patterns are stored in the bitstream in reverse order: pattern7 to pattern0
                for (int i = 7; i >= 0; i--) {
                  uint8_t pattern = rd.get_byte();
                  compression_dict.get()[i] = pattern;
                }
                BITSTREAM_DEBUG("write compression dictionary: " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[0]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[1]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[2]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[3]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[4]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[5]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[6]) << " " <<
                                "0x" << hex << setw(2) << setfill('0') << int(compression_dict.get()[7]));;
                if (check_crc)
                  rd.check_crc16();
            }
                break;
            case BitstreamCommand::LSC_INIT_ADDRESS:
                rd.skip_bytes(3);
                BITSTREAM_DEBUG("init address");
                break;
            case BitstreamCommand::LSC_PROG_INCR_CMP:
                // This is the main bitstream payload (compressed)
                BITSTREAM_DEBUG("Compressed bitstream found");
                if (!compression_dict)
                    throw BitstreamParseError("start of compressed bitstream data before compression dictionary was stored", rd.get_offset());
                // fall through
            case BitstreamCommand::LSC_PROG_INCR_RTI: {
                // This is the main bitstream payload
                if (!chip)
                    throw BitstreamParseError("start of bitstream data before chip was identified", rd.get_offset());
                bool reversed_frames;
                if (chip->info.family == "MachXO2")
                    reversed_frames = false;
                else if (chip->info.family == "ECP5")
                    reversed_frames = true;
                else
                    throw BitstreamParseError("Unknown chip family: " + chip->info.family);

                uint8_t params[3];
                rd.get_bytes(params, 3);
                BITSTREAM_DEBUG("settings: " << hex << setw(2) << int(params[0]) << " " << int(params[1]) << " "
                                             << int(params[2]));
                // I've only seen 0x81 for the ecp5 and 0x8e for the xo2 so far...
                bool check_crc = params[0] & 0x80U;
                // inverted value: a 0 means check after every frame
                bool crc_after_each_frame = check_crc && !(params[0] & 0x40U);
                // I don't know what these two are for I've seen both 1s (XO2) and both 0s (ECP5)
                // The names are from the ECP5 docs
                // bool include_dummy_bits = params[0] & 0x20U;
                // bool include_dummy_bytes = params[0] & 0x10U;
                size_t dummy_bytes = params[0] & 0x0FU;
                size_t frame_count = (params[1] << 8U) | params[2];
                BITSTREAM_NOTE("reading " << std::dec << frame_count << " config frames (with " << std::dec << dummy_bytes << " dummy bytes)");
                size_t bytes_per_frame = (chip->info.bits_per_frame + chip->info.pad_bits_after_frame +
                                          chip->info.pad_bits_before_frame) / 8U;
                // If compressed 0 bits are added to the stream before compression to make it 64 bit bounded, so
                // we should consider that space here but they shouldn't be copied to the output
                if (cmd == BitstreamCommand::LSC_PROG_INCR_CMP)
                    bytes_per_frame += (7 - ((bytes_per_frame - 1) % 8));
                unique_ptr<uint8_t[]> frame_bytes = make_unique<uint8_t[]>(bytes_per_frame);
                for (size_t i = 0; i < frame_count; i++) {
                    size_t idx = reversed_frames? (chip->info.num_frames - 1) - i : i;
                    if (cmd == BitstreamCommand::LSC_PROG_INCR_CMP)
                        rd.get_compressed_bytes(frame_bytes.get(), bytes_per_frame, compression_dict.get());
                    else
                        rd.get_bytes(frame_bytes.get(), bytes_per_frame);

                    for (int j = 0; j < chip->info.bits_per_frame; j++) {
                        size_t ofs = j + chip->info.pad_bits_after_frame;
                        chip->cram.bit(idx, j) = (char)
                            ((frame_bytes[(bytes_per_frame - 1) - (ofs / 8)] >> (ofs % 8)) & 0x01);
                    }
                    if (crc_after_each_frame || (check_crc && (i == frame_count-1)))
                      rd.check_crc16();
                    rd.skip_bytes(dummy_bytes);
                }
            }
                break;
            case BitstreamCommand::LSC_EBR_ADDRESS: {
                rd.skip_bytes(3);
                uint32_t data = rd.get_uint32();
                current_ebr = (data >> 11) & 0x3FF;
                addr_in_ebr = data & 0x7FF;
                chip->bram_data[current_ebr].resize(2048);
            }
                break;
            case BitstreamCommand::LSC_EBR_WRITE: {
                uint8_t params[3];
                rd.get_bytes(params, 3);
                int frame_count = (params[1] << 8U) | params[2];
                int frames_read = 0;

                while (frames_read < frame_count) {

                    if (addr_in_ebr >= 2048) {
                        addr_in_ebr = 0;
                        current_ebr++;
                        chip->bram_data[current_ebr].resize(2048);
                    }

                    auto &ebr = chip->bram_data[current_ebr];
                    frames_read++;
                    uint8_t frame[9];
                    rd.get_bytes(frame, 9);
                    ebr.at(addr_in_ebr+0) = (frame[0] << 1)        | (frame[1] >> 7);
                    ebr.at(addr_in_ebr+1) = (frame[1] & 0x7F) << 2 | (frame[2] >> 6);
                    ebr.at(addr_in_ebr+2) = (frame[2] & 0x3F) << 3 | (frame[3] >> 5);
                    ebr.at(addr_in_ebr+3) = (frame[3] & 0x1F) << 4 | (frame[4] >> 4);
                    ebr.at(addr_in_ebr+4) = (frame[4] & 0x0F) << 5 | (frame[5] >> 3);
                    ebr.at(addr_in_ebr+5) = (frame[5] & 0x07) << 6 | (frame[6] >> 2);
                    ebr.at(addr_in_ebr+6) = (frame[6] & 0x03) << 7 | (frame[7] >> 1);
                    ebr.at(addr_in_ebr+7) = (frame[7] & 0x01) << 8 | frame[8];
                    addr_in_ebr += 8;

                }
                rd.check_crc16();
            }
                break;
            case BitstreamCommand::SPI_MODE: {
                uint8_t spi_mode;
                rd.get_bytes(&spi_mode, 1);
                rd.skip_bytes(2);

                auto spimode = find_if(spi_modes.begin(), spi_modes.end(), [&](const pair<string, uint8_t> &fp){
                    return fp.second == spi_mode;
                });
                if (spimode == spi_modes.end())
                    throw runtime_error("bad SPI mode" + std::to_string(spi_mode));

                BITSTREAM_NOTE("SPI Mode " <<  spimode->first);
            }
                break;
            case BitstreamCommand::JUMP:
                rd.skip_bytes(3);
                BITSTREAM_DEBUG("Jump command");
                /* TODO: Parse address and SPI Flash read speed */
                rd.skip_bytes(4);
                break;
            case BitstreamCommand::DUMMY:
                break;
            default: BITSTREAM_FATAL("unsupported command 0x" << hex << setw(2) << setfill('0') << int(cmd),
                                     rd.get_offset());
        }
    }
    if (chip) {
        return *chip;
    } else {
        throw BitstreamParseError("failed to parse bitstream, no valid payload found");
    }
}

Bitstream Bitstream::generate_jump(uint32_t address) {
    BitstreamReadWriter wr;

    // Dummy bytes
    wr.insert_dummy(16);
    // Preamble
    wr.write_bytes(preamble.begin(), preamble.size());

    // Padding
    wr.insert_dummy(4);

    // Dummy control register
    wr.write_byte(uint8_t(BitstreamCommand::LSC_PROG_CNTRL0));
    wr.insert_zeros(3);
    wr.insert_zeros(4);

    // Jump command
    wr.write_byte(uint8_t(BitstreamCommand::JUMP));
    wr.insert_zeros(3);
    wr.write_byte(0x03); // TODO: Allow specifying SPI Flash read speed

    wr.write_byte(uint8_t((address >> 16UL) & 0xFF));
    wr.write_byte(uint8_t((address >> 8UL) & 0xFF));
    wr.write_byte(uint8_t(address & 0xFF));

    wr.insert_dummy(18);

    return Bitstream(wr.get(), std::vector<string>());
}

Bitstream Bitstream::serialise_chip(const Chip &chip, const map<string, string> options) {
    BitstreamReadWriter wr;
    // Preamble
    wr.write_bytes(preamble.begin(), preamble.size());
    // Padding
    wr.insert_dummy(4);

    if (options.count("spimode")) {
        auto spimode = find_if(spi_modes.begin(), spi_modes.end(), [&](const pair<string, uint8_t> &fp){
            return fp.first == options.at("spimode");
        });
        if (spimode == spi_modes.end())
            throw runtime_error("bad spimode option " + options.at("spimode"));

        wr.write_byte(uint8_t(BitstreamCommand::SPI_MODE));
        wr.write_byte(uint8_t(spimode->second));
        wr.insert_zeros(2);
    }

    // Reset CRC
    wr.write_byte(uint8_t(BitstreamCommand::LSC_RESET_CRC));
    wr.insert_zeros(3);
    wr.reset_crc16();
    // Verify ID
    wr.write_byte(uint8_t(BitstreamCommand::VERIFY_ID));
    wr.insert_zeros(3);
    wr.write_uint32(chip.info.idcode);
    // Set control reg 0 to 0x40000000
    wr.write_byte(uint8_t(BitstreamCommand::LSC_PROG_CNTRL0));
    wr.insert_zeros(3);
    uint32_t ctrl0  = chip.ctrl0;
    if (options.count("freq")) {
        auto freq = find_if(frequencies.begin(), frequencies.end(), [&](const pair<string, uint8_t> &fp){
            return fp.first == options.at("freq");
        });
        if (freq == frequencies.end())
            throw runtime_error("bad frequency option " + options.at("freq"));
        ctrl0 |= freq->second;
    }
    if (options.count("multiboot")) {
        if (options.at("multiboot") == "yes")
            ctrl0 |= multiboot_flag;
        else
            ctrl0 &= ~multiboot_flag;
    }
    wr.write_uint32(ctrl0);
    // Init address
    wr.write_byte(uint8_t(BitstreamCommand::LSC_INIT_ADDRESS));
    wr.insert_zeros(3);
    // Bitstream data
    wr.write_byte(uint8_t(BitstreamCommand::LSC_PROG_INCR_RTI));
    wr.write_byte(0x91); //CRC check, 1 dummy byte
    uint16_t frames = uint16_t(chip.info.num_frames);
    wr.write_byte(uint8_t((frames >> 8) & 0xFF));
    wr.write_byte(uint8_t(frames & 0xFF));
    size_t bytes_per_frame = (chip.info.bits_per_frame + chip.info.pad_bits_after_frame +
                              chip.info.pad_bits_before_frame) / 8U;
    unique_ptr<uint8_t[]> frame_bytes = make_unique<uint8_t[]>(bytes_per_frame);
    for (size_t i = 0; i < frames; i++) {
        fill(frame_bytes.get(), frame_bytes.get() + bytes_per_frame, 0x00);
        for (int j = 0; j < chip.info.bits_per_frame; j++) {
            size_t ofs = j + chip.info.pad_bits_after_frame;
            assert(((bytes_per_frame - 1) - (ofs / 8)) < bytes_per_frame);
            frame_bytes[(bytes_per_frame - 1) - (ofs / 8)] |=
                    (chip.cram.bit((chip.info.num_frames - 1) - i, j) & 0x01) << (ofs % 8);
        }
        wr.write_bytes(frame_bytes.get(), bytes_per_frame);
        wr.insert_crc16();
        wr.write_byte(0xFF);
    }
    // Post-bitstream space for SECURITY and SED (not used here)
    wr.insert_dummy(12);
    // Program Usercode
    wr.write_byte(uint8_t(BitstreamCommand::ISC_PROGRAM_USERCODE));
    wr.write_byte(0x80);
    wr.insert_zeros(2);
    wr.write_uint32(chip.usercode);
    wr.insert_crc16();
    for (const auto &ebr : chip.bram_data) {
        // BlockRAM initialisation

        // Set EBR address
        wr.write_byte(uint8_t(BitstreamCommand::LSC_EBR_ADDRESS));
        wr.insert_zeros(3);
        wr.write_uint32(ebr.first << 11UL);

        // Write EBR data
        wr.write_byte(uint8_t(BitstreamCommand::LSC_EBR_WRITE));
        wr.write_byte(0xD0); // Dummy/CRC config
        wr.write_byte(0x01); // 0x0100 = 256x 72-bit frames
        wr.write_byte(0x00);

        uint8_t frame[9];
        const auto &data = ebr.second;
        for (int addr_in_ebr = 0; addr_in_ebr < 2048; addr_in_ebr+=8) {
            frame[0] = data.at(addr_in_ebr+0) >> 1;
            frame[1] = (data.at(addr_in_ebr+0) & 0x01) << 7 | (data.at(addr_in_ebr+1) >> 2);
            frame[2] = (data.at(addr_in_ebr+1) & 0x03) << 6 | (data.at(addr_in_ebr+2) >> 3);
            frame[3] = (data.at(addr_in_ebr+2) & 0x07) << 5 | (data.at(addr_in_ebr+3) >> 4);
            frame[4] = (data.at(addr_in_ebr+3) & 0x0F) << 4 | (data.at(addr_in_ebr+4) >> 5);
            frame[5] = (data.at(addr_in_ebr+4) & 0x1F) << 3 | (data.at(addr_in_ebr+5) >> 6);
            frame[6] = (data.at(addr_in_ebr+5) & 0x3F) << 2 | (data.at(addr_in_ebr+6) >> 7);
            frame[7] = (data.at(addr_in_ebr+6) & 0x7F) << 1 | (data.at(addr_in_ebr+7) >> 8);
            frame[8] = data.at(addr_in_ebr+7);
            wr.write_bytes(frame, 9);
        }
        wr.insert_crc16();
    }
    // Program DONE
    wr.write_byte(uint8_t(BitstreamCommand::ISC_PROGRAM_DONE));
    wr.insert_zeros(3);
    // Trailing padding
    wr.insert_dummy(4);
    return Bitstream(wr.get(), chip.metadata);
}

void Bitstream::write_bit(ostream &out) {
    // Write metadata header
    out.put(char(0xFF));
    out.put(0x00);
    for (const auto &str : metadata) {
        out << str;
        out.put(0x00);
    }
    out.put(char(0xFF));
    // Dump raw bitstream
    out.write(reinterpret_cast<const char *>(&(data[0])), data.size());
}

vector<uint8_t> Bitstream::get_bytes() {
    vector<uint8_t> bytes;
    bytes.push_back(0xFF);
    bytes.push_back(0x00);
    for (const auto &str : metadata) {
        copy(str.begin(), str.end(), back_inserter(bytes));
        bytes.push_back(0x00);
    }
    bytes.push_back(0xFF);
    copy(data.begin(), data.end(), back_inserter(bytes));
    return bytes;
}

void Bitstream::write_bin(ostream &out) {
    out.write(reinterpret_cast<const char *>(&(data[0])), data.size());
}

Bitstream Bitstream::read_bit_py(string file) {
    ifstream inf(file, ios::binary);
    if (!inf)
        throw runtime_error("failed to open input file " + file);
    return read_bit(inf);
}

void Bitstream::write_bit_py(string file) {
    ofstream ouf(file, ios::binary);
    if (!ouf)
        throw runtime_error("failed to open output file " + file);
    write_bit(ouf);
}

BitstreamParseError::BitstreamParseError(const string &desc) : runtime_error(desc.c_str()), desc(desc), offset(-1) {}

BitstreamParseError::BitstreamParseError(const string &desc, size_t offset) : runtime_error(desc.c_str()), desc(desc),
                                                                              offset(int(offset)) {}

const char *BitstreamParseError::what() const noexcept {
    ostringstream ss;
    ss << "Bitstream Parse Error: ";
    ss << desc;
    if (offset != -1)
        ss << " [at 0x" << hex << offset << "]";
    return strdup(ss.str().c_str());
}

}
