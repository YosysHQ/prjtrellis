#include "ChipConfig.hpp"
#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "DatabasePath.hpp"
#include "Tile.hpp"
#include "BitDatabase.hpp"
#include "version.hpp"
#include "wasmexcept.hpp"
#include <iostream>
#include <boost/program_options.hpp>
#include <stdexcept>
#include <streambuf>
#include <fstream>
#include <iomanip>

using namespace std;

uint8_t reverse_byte(uint8_t byte) {
    uint8_t rev = 0;
    for (int i = 0; i < 8; i++)
        if (byte & (1 << i))
            rev |= (1 << (7 - i));
    return rev;
}

uint32_t convert_hexstring(std::string value_str)
{
    return uint32_t(strtoul(value_str.c_str(), nullptr, 0));
}

uint16_t calc_checksum(std::string bytes)
{
    uint16_t checksum = 0;

    for(auto &c: bytes)
    {
        checksum += c;
    }

    return checksum;
}

uint32_t get_num_config_fuses(Trellis::ChipInfo &ci) {
    if(ci.name == "LCMXO2-256") {
        return (575 + 0 + 1)*128; // No UFM, 1 dummy page at end.
    } else if(ci.name == "LCMXO2-640") {
        return (1151 + 191 + 1)*128; // UFM is 0 bytes after end of CFG, 1 dummy page at end.
    } else if(ci.name == "LCMXO2-1200" || ci.name == "LCMXO2-640U") {
        return (2175 + 511 + 1)*128; // UFM is 0 bytes after end of CFG, 1 dummy page at end.
    } else if(ci.name == "LCMXO2-2000" || ci.name == "LCMXO2-1200U") {
        return (3198 + 639 + 1)*128; // UFM is 0 bytes after end of CFG, 1 dummy page at end.
    } else if(ci.name == "LCMXO2-4000" || ci.name == "LCMXO2-2000U") {
        return (5758 + 767 + 1)*128; // UFM is 0 bytes after end of CFG, 1 dummy page at end.
    } else if(ci.name == "LCMXO2-7000") {
        return (9211 + 1 + 2046 + 2)*128; // UFM is 16 bytes after end of CFG, 2 dummy pages at end.
    } else {
        throw runtime_error(fmt("Can not extract number of config fuses from FPGA family " << ci.name));
    }
}

int num_digits(uint32_t num) {
    int count = 0;
    do {
        num /= 10;
        count++;
    } while(num != 0);

    return count;
}

int main(int argc, char *argv[])
{
    using namespace Trellis;
    namespace po = boost::program_options;

    std::string database_folder = get_database_path();

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
    options.add_options()("db", po::value<std::string>(), "Trellis database folder location");
    options.add_options()("usercode", po::value<uint32_t>(), "USERCODE to set in bitstream");
    options.add_options()("idcode", po::value<std::string>(), "IDCODE to override in bitstream");
    options.add_options()("freq", po::value<std::string>(), "config frequency in MHz");
    options.add_options()("svf", po::value<std::string>(), "output SVF file");
    options.add_options()("svf-rowsize", po::value<int>(), "SVF row size in bits (default 8000)");
    options.add_options()("jed", po::value<std::string>(), "output JED file");
    options.add_options()("jed-note", po::value<vector<std::string>>(), "emit NOTE field in JED file");
    options.add_options()("compress", "compress bitstream to reduce size");
    options.add_options()("spimode", po::value<std::string>(), "SPI Mode to use (fast-read, dual-spi, qspi)");
    options.add_options()("background", "enable background reconfiguration in bitstream");
    options.add_options()("delta", po::value<std::string>(), "create a delta partial bitstream given a reference config");
    options.add_options()("bootaddr", po::value<std::string>(), "set next BOOTADDR in bitstream and enable multi-boot");
    po::positional_options_description pos;
    options.add_options()("input", po::value<std::string>()->required(), "input textual configuration");
    pos.add("input", 1);
    options.add_options()("bit", po::value<std::string>(), "output bitstream file");
    pos.add("bit", 1);
    options.add_options()("version", "show current version and exit");

    po::variables_map vm;

    try {
        po::parsed_options parsed = po::command_line_parser(argc, argv).options(options).positional(pos).run();
        po::store(parsed, vm);

        if (vm.count("version")) {
            cerr << "Project Trellis ecppack Version " << git_describe_str << endl;
            return 0;
        }

        po::notify(vm);
    }
    catch (po::required_option& e) {
        cerr << "Error: input file is mandatory." << endl << endl;
        goto help;
    }
    catch (std::exception& e) {
        cerr << "Error: " << e.what() << endl << endl;
        goto help;
    }

    if (vm.count("help")) {
help:
        cerr << "Project Trellis - Open Source Tools for ECP5 FPGAs" << endl;
        cerr << "Version " << git_describe_str << endl;
        cerr << argv[0] << ": ECP5 bitstream packer" << endl;
        cerr << endl;
        cerr << "Copyright (C) 2018 gatecat <gatecat@ds0.me>" << endl;
        cerr << endl;
        cerr << "Usage: " << argv[0] << " input.config [output.bit] [options]" << endl;
        cerr << options << endl;
        return vm.count("help") ? 0 : 1;
    }

    ifstream config_file(vm["input"].as<string>());
    if (!config_file) {
        cerr << "Failed to open input file" << endl;
        return 1;
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

    string textcfg((std::istreambuf_iterator<char>(config_file)), std::istreambuf_iterator<char>());

    ChipConfig cc;
    try {
        cc = ChipConfig::from_string(textcfg);
    } catch (runtime_error &e) {
        cerr << "Failed to process input config: " << e.what() << endl;
        return 1;
    }

    Chip c = cc.to_chip();
    if (vm.count("usercode"))
        c.usercode = vm["usercode"].as<uint32_t>();

    if (vm.count("idcode")) {
        string idcode_str = vm["idcode"].as<string>();
        uint32_t idcode = uint32_t(strtoul(idcode_str.c_str(), nullptr, 0));
        if (idcode == 0) {
            cerr << "Invalid idcode: " << idcode_str << endl;
            return 1;
        }
        c.info.idcode = idcode;
    }

    map<string, string> bitopts;

    // Apply options passed from nextpnr via SYSCONFIG
    if (cc.sysconfig.count("MCCLK_FREQ")) {
        std::string freq = cc.sysconfig.at("MCCLK_FREQ");
        if (freq == "62")
            freq = "62.0";
        bitopts["freq"] = freq;
    }

    if (cc.sysconfig.count("COMPRESS_CONFIG") && cc.sysconfig.at("COMPRESS_CONFIG") == "ON")
        bitopts["compress"] = "yes";

    // Override with command line options
    if (vm.count("freq"))
        bitopts["freq"] = vm["freq"].as<string>();

    if (vm.count("spimode"))
        bitopts["spimode"] = vm["spimode"].as<string>();

    if (vm.count("compress"))
        bitopts["compress"] = "yes";

    if (vm.count("background")) {
        auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, "EFB0_PICB0"});
        auto esb = tile_db->get_data_for_enum("SYSCONFIG.BACKGROUND_RECONFIG");
        auto tile = c.get_tiles_by_type("EFB0_PICB0");
        for (const auto &bit : esb.options["ON"].bits)
            tile[0]->cram.set_bit(bit.frame, bit.bit, bit.inv ? 0 : 1);
        bitopts["background"] = "yes";
    }

    if (vm.count("bootaddr")) {
        uint32_t bootaddr = convert_hexstring(vm["bootaddr"].as<string>());

        if (bootaddr & 0xffff) {
            cerr << "Error: Boot Address must be 64k aligned !" << endl;
            return 1;
        }

        bootaddr = (bootaddr & 0x00ff0000) >> 16;

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
                bool value = (bootaddr & (1 << j)) > 0;
                tile[0]->cram.set_bit(bit.frame, bit.bit, value);
            }
        }

        bitopts["multiboot"] = "yes";
    }

    bool partial_mode = false;
    vector<uint32_t> partial_frames;
    if (vm.count("delta")) {
        ifstream delta_file(vm["delta"].as<string>());
        if (!delta_file) {
            cerr << "Failed to open reference config file" << endl;
            return 1;
        }
        string refcfg((std::istreambuf_iterator<char>(delta_file)), std::istreambuf_iterator<char>());

        ChipConfig ref_cc;
        try {
            ref_cc = ChipConfig::from_string(refcfg);
        } catch (runtime_error &e) {
            cerr << "Failed to process reference config: " << e.what() << endl;
            return 1;
        }
        Chip ref_c = ref_cc.to_chip();
        for (int frame = 0; frame < c.cram.frames(); frame++) {
            if (ref_c.cram.data->at(frame) != c.cram.data->at(frame)) {
                partial_frames.push_back(frame);
            }
        }

        partial_mode = true;
    }

    Bitstream b = partial_mode ? Bitstream::serialise_chip_partial(c, partial_frames, bitopts) : Bitstream::serialise_chip(c, bitopts);
    if (vm.count("bit")) {
        ofstream bit_file(vm["bit"].as<string>(), ios::binary);
        if (!bit_file) {
            cerr << "Failed to open output file" << endl;
            return 1;
        }
        b.write_bit(bit_file);
    }

    if (vm.count("svf")) {
        // Create JTAG bitstream without SPI flash related settings, as these
        // seem to confuse the chip sometimes when configuring over JTAG
        if (!bitopts.empty() && !(bitopts.size() == 1 && bitopts.count("compress"))) {
            bitopts.erase("spimode");
            bitopts.erase("freq");
            b = Bitstream::serialise_chip(c, bitopts);
        }

        vector<uint8_t> bitstream = b.get_bytes();
        int max_row_size = 8000;
        if (vm.count("svf-rowsize"))
            max_row_size = vm["svf-rowsize"].as<int>();
        if ((max_row_size % 8) != 0 || max_row_size <= 0) {
            cerr << "SVF row size must be an exact positive number of bytes" << endl;
            return 1;
        }
        ofstream svf_file(vm["svf"].as<string>());
        if (!svf_file) {
            cerr << "Failed to open output SVF file" << endl;
            return 1;
        }
        svf_file << "HDR\t0;" << endl;
        svf_file << "HIR\t0;" << endl;
        svf_file << "TDR\t0;" << endl;
        svf_file << "TIR\t0;" << endl;
        svf_file << "ENDDR\tDRPAUSE;" << endl;
        svf_file << "ENDIR\tIRPAUSE;" << endl;
        svf_file << "STATE\tIDLE;" << endl;
        svf_file << "SIR\t8\tTDI  (E0);" << endl;
        svf_file << "SDR\t32\tTDI  (00000000)" << endl;
        svf_file << "\t\t\tTDO  (" << setw(8) << hex << uppercase << setfill('0') << c.info.idcode << ")" << endl;
        svf_file << "\t\t\tMASK (FFFFFFFF);" << endl;
        svf_file << endl;
        if (!partial_mode) {
            svf_file << "SIR\t8\tTDI  (1C);" << endl;
            svf_file << "SDR\t510\tTDI  (3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" << endl;
            svf_file << "\t\t\t\tFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF);" << endl;
            svf_file << endl;
            svf_file << "SIR\t8\tTDI  (C6);" << endl;
            svf_file << "SDR\t8\tTDI  (00);" << endl;
            svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
            svf_file << endl;
            svf_file << "SIR\t8\tTDI  (0E);" << endl;
            svf_file << "SDR\t8\tTDI  (01);" << endl;
            svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
            svf_file << endl;
            svf_file << "SIR\t8\tTDI  (3C);" << endl;
            svf_file << "SDR\t32\tTDI  (00000000)" << endl;
            svf_file << "\t\t\tTDO  (00000000)" << endl;
            svf_file << "\t\t\tMASK (0000B000);" << endl;
            svf_file << endl;
        } else {
            svf_file << "SIR\t8\tTDI  (79);" << endl;
            svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
            svf_file << "SIR\t8\tTDI  (74);" << endl;
            svf_file << "SDR\t8\tTDI  (00);" << endl;
            svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
        }
        svf_file << "SIR\t8\tTDI  (46);" << endl;
        svf_file << "SDR\t8\tTDI  (01);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
        svf_file << endl;
        svf_file << "SIR\t8\tTDI  (7A);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
        size_t i = 0;
        while(i < bitstream.size()) {
           size_t len = min(size_t(max_row_size / 8), bitstream.size() - i);
           if (len == 0)
               break;
           svf_file << "SDR\t" << setw(0) << dec << (8 * len) << "\tTDI  (";
           svf_file << hex << uppercase << setw(2) << setfill('0');
           for (int j = len - 1; j >= 0; j--) {
                svf_file << setw(2) << unsigned(reverse_byte(uint8_t(bitstream[j + i])));
                if (j % 40 == 0 && j != 0)
                    svf_file << endl << "\t\t\t";
           }
           svf_file << ");" << endl;
           i += len;
        }
        if (!partial_mode) {
            svf_file << endl;
            svf_file << "SIR\t8\tTDI  (FF);" << endl;
            svf_file << "RUNTEST\tIDLE\t100 TCK\t1.00E-02 SEC;" << endl;
            svf_file << endl;
            svf_file << "SIR\t8\tTDI  (C0);" << endl;
            svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-03 SEC;" << endl;
            svf_file << "SDR\t32\tTDI  (00000000)" << endl;
            svf_file << "\t\t\tTDO  (00000000)" << endl;
            svf_file << "\t\t\tMASK (FFFFFFFF);" << endl;
            svf_file << endl;
        }
        svf_file << "SIR\t8\tTDI  (26);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t2.00E-01 SEC;" << endl;
        svf_file << endl;
        svf_file << "SIR\t8\tTDI  (FF);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-03 SEC;" << endl;
        svf_file << endl;
        if (!partial_mode) {
            svf_file << "SIR\t8\tTDI  (3C);" << endl;
            svf_file << "SDR\t32\tTDI  (00000000)" << endl;
            svf_file << "\t\t\tTDO  (00000100)" << endl;
            svf_file << "\t\t\tMASK (00002100);" << endl;
        }
    }

    if (vm.count("jed")) {
        // Create JTAG bitstream without SPI flash related settings, as these
        // seem to confuse the chip sometimes when configuring over JTAG
        if (!bitopts.empty() && !(bitopts.size() == 1 && bitopts.count("compress"))) {
            bitopts.erase("spimode");
            bitopts.erase("freq");
            b = Bitstream::serialise_chip(c, bitopts);
        }

        vector<uint8_t> bitstream = b.get_bytes();
        ofstream jed_file(vm["jed"].as<string>(), ios_base::binary);
        uint16_t checksum = 0;
        uint16_t full_checksum = 0;

        jed_file << "\x02*" << endl; // STX plus "design specification" (not filled in).
        full_checksum += calc_checksum("\x02*\n");

        if (vm.count("jed-note")) {
            ostringstream note_field;
            for(auto &n: vm["jed-note"].as<vector<string>>()) {
                note_field << "NOTE " << n << "*" << endl;
                full_checksum += calc_checksum(note_field.str());
                jed_file << note_field.str();
            }
        }

        ostringstream fusecnt_field;
        uint32_t fusecnt;
        try {
            fusecnt = get_num_config_fuses(c.info);
        } catch (runtime_error &e) {
            cerr << "Failed to extract JED file size: " << e.what() << endl;
            return 1;
        }
        
        // TODO: QP (package information not implied in textual representation).
        fusecnt_field << "QF" << fusecnt << '*' << endl;
        full_checksum += calc_checksum(fusecnt_field.str());
        jed_file << fusecnt_field.str();
        
        jed_file << "G0*" << endl; // Security fuse not supported yet.
        full_checksum += calc_checksum("G0*\n");
        jed_file << "F0*" << endl; // Default fuse value.
        full_checksum += calc_checksum("F0*\n");

        // The JEDEC spec says leading 0s are optional. My own experience is
        // that some programmers require leading 0s.
        ostringstream list_field;
        list_field << "L" << setw(num_digits(fusecnt)) << setfill('0') << 0 << endl;
        full_checksum += calc_checksum(list_field.str());
        jed_file << list_field.str();

        // Strip the leading comment- it wastes precious fuse space and
        // some programmers (e.g STEP-MXO2) even rely on the preamble being
        // the first bytes.
        vector<uint8_t> preamble = {0xFF, 0xFF, 0xBD, 0xB3, 0xFF, 0xFF };
        auto start_iter = search(begin(bitstream), end(bitstream), begin(preamble), end(preamble));

        if(start_iter == end(bitstream)) {
            cerr << "Could not extract preamble from bitstream" << endl;
            return 1;
        }

        auto start_offs = start_iter - bitstream.begin();

        size_t i = 0;
        while(i < fusecnt/8) {
            if(i < bitstream.size()) {
                size_t len = min(size_t(16), bitstream.size() - i);

                for (unsigned int j = 0; j < len; j++) {
                    uint8_t byte = uint8_t(bitstream[j + i + start_offs]);
                    checksum += reverse_byte(byte);
                    full_checksum += calc_checksum(bitset<8>{byte}.to_string());
                    jed_file << std::bitset<8>{byte};
                }

                // Pad to 128 bits if at end of bitstream.
                if(len < 16) {
                    for(unsigned int k = 0; k < 16 - len; k++) {
                        uint8_t byte = 0;
                        checksum += reverse_byte(byte);
                        full_checksum += calc_checksum(std::bitset<8>{byte}.to_string());
                        jed_file << std::bitset<8>{byte};
                    }
                }
                

            } else {
                // Fill in remaining 128-bit rows
                for(unsigned int j = 0; j < 16; j++) {
                    uint8_t byte = 0;
                    checksum += reverse_byte(byte);
                    full_checksum += calc_checksum(std::bitset<8>{byte}.to_string());
                    jed_file << std::bitset<8>{byte};
                }
            }

            jed_file << endl;
            full_checksum += calc_checksum("\n");
            i += 16;
        }

        jed_file << "*" << endl;
        full_checksum += calc_checksum("*\n");

        ostringstream checksum_field;
        checksum_field << "C" << hex << uppercase << setfill('0') << setw(4) << checksum << '*' << endl;
        full_checksum += calc_checksum(checksum_field.str());
        jed_file << checksum_field.str();

        full_checksum += calc_checksum("\x03");
        jed_file << "\x03" << hex << uppercase << setw(4) << setfill('0') << full_checksum << endl;
    }

    return 0;
}
