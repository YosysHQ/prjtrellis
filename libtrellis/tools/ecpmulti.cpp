#include "ChipConfig.hpp"
#include "BitDatabase.hpp"
#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "Tile.hpp"
#include <iostream>
#include <boost/program_options.hpp>
#include <stdexcept>
#include <streambuf>
#include <fstream>


/* TODO:
 * Support golden image properly
 * Cleanup logging
 * Verify inputs before starting, including that there's no overlap.
 * Fill with 0xFF instead of 0x00
 * Possibly intel hex file output instead?
 * Error checking!
 * Allow specifying inputs/addresses in any order and sort them correctly
 *   and inject golden image at the suitable position
*/
using namespace std;

boost::optional<uint32_t> convert_hexstring(std::string value_str)
{
    boost::optional<uint32_t> ret;
    uint32_t value = uint32_t(strtoul(value_str.c_str(), nullptr, 0));
    if (value != 0)
        ret = value;

    return ret;
}


int main(int argc, char *argv[])
{
    using namespace Trellis;
    namespace po = boost::program_options;

    std::string database_folder = TRELLIS_PREFIX "/share/trellis/database";
    uint32_t flash_size_bytes = 0;
    boost::optional<uint32_t> input_idcode;
    boost::optional<uint32_t> output_idcode;
    boost::optional<uint32_t> idcode;
    uint32_t nextaddr = 0;
    std::array<char, 4096> fillpattern;

    std::fill(fillpattern.begin(), fillpattern.end(), 0xff);

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
    options.add_options()("db", po::value<std::string>(), "Trellis database folder location");
    options.add_options()("input", po::value<std::vector<std::string>>()->required(), "input bitstream file 0..N");
    options.add_options()("address", po::value<std::vector<std::string>>()->required(), "address to place next bitstream at [1..N]");
    options.add_options()("flashsize", po::value<std::uint32_t>()->required(), "Flash size in Mbits, e.g. 2, 4, 8, ..., 128");
    options.add_options()("input-idcode", po::value<std::string>(), "IDCODE override for input file");
    options.add_options()("output-idcode", po::value<std::string>(), "IDCODE override in output bitstreams");

    po::positional_options_description pos;
    options.add_options()("output", po::value<std::string>()->required(), "output bitstream file");
    pos.add("output", 1);


    po::variables_map vm;
    try {
        po::parsed_options parsed = po::command_line_parser(argc, argv).options(options).positional(pos).run();
        po::store(parsed, vm);
        po::notify(vm);
    }
    catch (std::exception &e) {
        cerr << e.what() << endl << endl;
        goto help;
    }

    if (vm.count("help")) {
        help:
        cerr << "Project Trellis - Open Source Tools for ECP5 FPGAs" << endl;
        cerr << "ecpmulti: ECP5 multiboot bitstream assembler" << endl;
        cerr << endl;
        cerr << "Copyright (C) 2019 Jens Andersen <jens.andersen@gmail.com>" << endl;
        cerr << endl;
        cerr << options << endl;
        return vm.count("help") ? 0 : 1;
    }

    if (vm.count("flashsize")) {
        uint32_t flash_size_mbit = vm["flashsize"].as<uint32_t>();
        flash_size_bytes = flash_size_mbit * 1024* 1024 / 8;
        cout << "Using flashsize " << flash_size_mbit << "(" << flash_size_bytes << " bytes)" << endl;
    }

    auto inputs = vm.at("input").as<std::vector<std::string>>();
    auto addresses = vm.at("address").as<std::vector<std::string>>();

    if (inputs.size() != (addresses.size() + 1)) {
        cerr << "Inputs " << inputs.size() << " offsets " << addresses.size() << endl;
        cerr << "There must be one address specified per extra bitstream (>1)" << endl;
        return 1;
    }

    if (vm.count("input-idcode")) {
        input_idcode = convert_hexstring(vm.at("input-idcode").as<std::string>());
    }

    if (vm.count("output-idcode")) {
        output_idcode = convert_hexstring(vm.at("output-idcode").as<std::string>());
    }

    if (vm.count("db")) {
        database_folder = vm["db"].as<string>();
    }

    try {
        load_database(database_folder);
    } catch (runtime_error &e) {
        cerr << "Failed to load Trellis database: " << e.what() << endl;
        return 1;
    }

    ofstream out_file(vm["output"].as<string>(), ofstream::trunc);
    if (!out_file) {
        cerr << "Failed to open output file" << endl;
        return 1;
    }

    const map<string, string> bs_options = {{"multiboot", "yes"} };

    for(uint32_t i = 0; i < inputs.size(); i++) {
        ifstream bitfile;
        string filename = inputs.at(i);
        uint32_t address = nextaddr << 16;

        if (address > flash_size_bytes || address < out_file.tellp()) {
            cerr << "Addresses must be ordered and smaller than flash size" << endl;
            return 1;
        }

        cout << "Processing " << filename << " for address " << hex << address << endl;
        bitfile.open(inputs[i], ios::binary);

        Bitstream bs = Bitstream::read_bit(bitfile);
        Chip c = bs.deserialise_chip(input_idcode);
        if (!idcode.is_initialized())
            idcode = c.info.idcode;

        if (idcode != c.info.idcode) {
            cerr << "All input files must be for the same model (" << *idcode << " != " << c.info.idcode << ")" << endl;
            return 1;
        }

        if (i < addresses.size()) {
            string offset_str = addresses.at(i);
            boost::optional<uint32_t> next_addr_val = convert_hexstring(offset_str);

            if (!next_addr_val.is_initialized()) {
                cerr << "Invalid offset: " << offset_str << endl;
                return 1;
            }
            nextaddr = ((*next_addr_val) & 0x00FF0000) >> 16;
        } else
            /* Point back to first bitstream */
            nextaddr = 0;

        auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, "EFB1_PICB1"});
        WordSettingBits wsb = tile_db->get_data_for_setword("BOOTADDR");
        auto tile = c.get_tiles_by_type("EFB1_PICB1");
        if (tile.size() != 1) {
            cerr << "EFB1_PICB1 Frame is wrong size. Can't proceed" << endl;
            return 1;
        }


        for(uint32_t j=0; j < wsb.bits.size(); j++) {
            auto bg = wsb.bits.at(j);
            for (auto bit :  bg.bits) {
                bool value = (nextaddr & (1 << j)) > 0;
                tile[0]->cram.set_bit(bit.frame, bit.bit, value);
            }
        }

        uint32_t fill_size = address - out_file.tellp();
        while(fill_size > 0) {
            uint32_t batch_size = std::min(fill_size, (uint32_t)4096);
            out_file.write(fillpattern.data(), batch_size);
            fill_size -= batch_size;
        }

        /* Pad with 256 byte 0xFF to match Diamond tools.
         * TN1216 indicates it has to do with garbage bytes coming out of SPI Flash sometimes */
        out_file.write(fillpattern.data(), 256);

        if (output_idcode.is_initialized()) {
            c.info.idcode = *output_idcode;
        }
        bs = Bitstream::serialise_chip(c, bs_options);
        bs.write_bit(out_file);
    }


    /* TODO: Support golden image
     * 1) Inject golden image into right area of final bitfile
     * 2) Use Bitstream::generate_jump(golden_addr) to generate a Bitstream
     * 3) At end of file, (flash_size - 0xFF) write jump bitstream
     */

    out_file.flush();
    out_file.close();
    return 0;
}
