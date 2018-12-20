#include "ChipConfig.hpp"
#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
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

int main(int argc, char *argv[])
{
    using namespace Trellis;
    namespace po = boost::program_options;

    std::string database_folder = TRELLIS_PREFIX "/share/trellis/database";

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
    options.add_options()("db", po::value<std::string>(), "Trellis database folder location");
    options.add_options()("usercode", po::value<uint32_t>(), "USERCODE to set in bitstream");
    options.add_options()("idcode", po::value<std::string>(), "IDCODE to override in bitstream");
    options.add_options()("freq", po::value<std::string>(), "config frequency in MHz");
    options.add_options()("svf", po::value<std::string>(), "output SVF file");
    options.add_options()("svf-rowsize", po::value<int>(), "SVF row size in bits (default 8000)");

    po::positional_options_description pos;
    options.add_options()("input", po::value<std::string>()->required(), "input textual configuration");
    pos.add("input", 1);
    options.add_options()("bit", po::value<std::string>(), "output bitstream file");
    pos.add("bit", 1);

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
        cerr << "ecppack: ECP5 bitstream packer" << endl;
        cerr << endl;
        cerr << "Copyright (C) 2018 David Shah <david@symbioticeda.com>" << endl;
        cerr << endl;
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

    if (vm.count("freq"))
        bitopts["freq"] = vm["freq"].as<string>();

    Bitstream b = Bitstream::serialise_chip(c, bitopts);
    if (vm.count("bit")) {
        ofstream bit_file(vm["bit"].as<string>(), ios::binary);
        if (!bit_file) {
            cerr << "Failed to open output file" << endl;
            return 1;
        }
        b.write_bit(bit_file);
    }

    if (vm.count("svf")) {
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
        svf_file << "SIR\t8\tTDI  (1C);" << endl;
        svf_file << "SDR\t510\tTDI  (3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" << endl;
        svf_file << "\t\t\t\tFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF);" << endl;
        svf_file << endl;
        svf_file << "SIR\t8\tTDI  (C6);" << endl;
        svf_file << "SDR\t8\tTDI  (00);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-02 SEC;" << endl;
        svf_file << endl;
        svf_file << "SIR\t8\tTDI  (3C);" << endl;
        svf_file << "SDR\t32\tTDI  (00000000)" << endl;
        svf_file << "\t\t\tTDO  (00000000)" << endl;
        svf_file << "\t\t\tMASK (0000B000);" << endl;
        svf_file << endl;
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
        svf_file << "SIR\t8\tTDI  (26);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t2.00E-01 SEC;" << endl;
        svf_file << endl;
        svf_file << "SIR\t8\tTDI  (FF);" << endl;
        svf_file << "RUNTEST\tIDLE\t2 TCK\t1.00E-03 SEC;" << endl;
        svf_file << endl;
        svf_file << "SIR\t8\tTDI  (3C);" << endl;
        svf_file << "SDR\t32\tTDI  (00000000)" << endl;
        svf_file << "\t\t\tTDO  (00000100)" << endl;
        svf_file << "\t\t\tMASK (00002100);" << endl;
    }

    return 0;
}
