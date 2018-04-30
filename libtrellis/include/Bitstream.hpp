#ifndef LIBTRELLIS_LATTICEBITSTREAM_H
#define LIBTRELLIS_LATTICEBITSTREAM_H

#include <cstdint>
#include <memory>
#include <iostream>
#include <vector>
#include <string>
#include <runtime_error>

using namespace std;

namespace Trellis {
    enum class BitstreamCommands : uint8_t {
        LSC_RESET_CRC           = 0b00111011,
        VERIFY_ID               = 0b11100010,
        LSC_WRITE_COMP_DIC      = 0b00000010,
        LSC_PROG_CNTRL0         = 0b00100010,
        LSC_INIT_ADDRESS        = 0b01000110,
        LSC_PROG_INCR_CMP       = 0b10111000,
        LSC_PROG_INCR_RTI       = 0b10000010,
        LSC_PROG_SED_CRC        = 0b10100010,
        ISC_PROGRAM_SECURITY    = 0b11001110,
        ISC_PROGRAM_USERCODE    = 0b11000010,
        LSC_EBR_ADDRESS         = 0b11110110,
        LSC_EBR_WRITE           = 0b10110010,
        ISC_PROGRAM_DONE        = 0b01011110,
        DUMMY                   = 0b11111111,
    };

    class Chip;

    // This represents a low level bitstream, as nothing more than an
    // array of bytes and helper functions for common tasks
    class Bitstream {
    public:
        // Read a Lattice .bit file (metadata + bitstream)
        static Bitstream ReadBIT(istream &in);
        // Serialise a Chip back to a bitstream
        static Bitstream SerialiseChip(Chip &chip);
        // Deserialise a bitstream to a Chip
        Chip DeserialiseChip();
        // Write a Lattice .bit file (metadata + bitstream)
        void WriteBIT(ostream &out);
        // Write a Lattice .bin file (bitstream only, for flash prog.)
        void WriteBIN(ostream &out);
    private:
        // Raw bitstream data
        unique_ptr<uint8_t> data;
        // Lattice BIT file metadata
        vector<string> metatdata;
        // Private constructor
        Bitstream(unique_ptr<uint8_t> data, const vector<string> &metadata);
    };

    // Represents an error that occurs while parsing the bitstream
    class BitstreamParseError : runtime_error {
    public:
        BitstreamParseError(const string &desc);
        BitstreamParseError(const string &desc, size_t offset);
        const char *what() const noexcept override;
    private:
        string desc;
        size_t offset;
    };
};

#endif //LIBTRELLIS_LATTICEBITSTREAM_H
