#ifndef LIBTRELLIS_BITSTREAM_H
#define LIBTRELLIS_BITSTREAM_H

#include <cstdint>
#include <memory>
#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <map>
#include <boost/optional.hpp>

using namespace std;

namespace Trellis {
enum class BitstreamCommand : uint8_t {
    SPI_MODE = 0b01111001,
    JUMP = 0b01111110,
    LSC_RESET_CRC = 0b00111011,
    VERIFY_ID = 0b11100010,
    LSC_WRITE_COMP_DIC = 0b00000010,
    LSC_PROG_CNTRL0 = 0b00100010,
    LSC_INIT_ADDRESS = 0b01000110,
    LSC_PROG_INCR_CMP = 0b10111000,
    LSC_PROG_INCR_RTI = 0b10000010,
    LSC_PROG_SED_CRC = 0b10100010,
    ISC_PROGRAM_SECURITY = 0b11001110,
    ISC_PROGRAM_USERCODE = 0b11000010,
    LSC_EBR_ADDRESS = 0b11110110,
    LSC_EBR_WRITE = 0b10110010,
    ISC_PROGRAM_DONE = 0b01011110,
    DUMMY = 0b11111111,
};

class Chip;


// This represents a low level bitstream, as nothing more than an
// array of bytes and helper functions for common tasks
class Bitstream {
public:
    // Read a Lattice .bit file (metadata + bitstream)
    // Note that string variants take a filename, for ease of Python binding
    static Bitstream read_bit(istream &in);

    // Python variant of the above, takes filename instead of istream
    static Bitstream read_bit_py(string file);

    // Serialise a Chip back to a bitstream
    static Bitstream serialise_chip(const Chip &chip, const map<string, string> options);
    static Bitstream generate_jump(uint32_t address);

    // Deserialise a bitstream to a Chip
    Chip deserialise_chip();
    Chip deserialise_chip(boost::optional<uint32_t> idcode = boost::optional<uint32_t>());

    // Write a Lattice .bit file (metadata + bitstream)
    void write_bit(ostream &out);

    // Python variant of the above, takes filename instead of ostream
    void write_bit_py(string file);

    // Write bitstream as a vector of bytes
    vector<uint8_t> get_bytes();

    // Write a Lattice .bin file (bitstream only, for flash prog.)
    void write_bin(ostream &out);

    // Raw bitstream data
    vector<uint8_t> data;
    // Lattice BIT file metadata
    vector<string> metadata;
private:

    // Private constructor
    Bitstream(const vector<uint8_t> &data, const vector<string> &metadata);
};

// Represents an error that occurs while parsing the bitstream
class BitstreamParseError : runtime_error {
public:
    explicit BitstreamParseError(const string &desc);

    BitstreamParseError(const string &desc, size_t offset);

    const char *what() const noexcept override;

private:
    string desc;
    int offset;
};
}

#endif //LIBTRELLIS_BITSTREAM_H
