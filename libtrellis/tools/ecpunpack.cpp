#include "ChipConfig.hpp"
#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include <iostream>
#include <boost/optional.hpp>
#include <boost/program_options.hpp>
#include <stdexcept>
#include <streambuf>
#include <fstream>

using namespace std;

int main(int argc, char *argv[])
{
    using namespace Trellis;
    namespace po = boost::program_options;
    boost::optional<uint32_t> idcode;

    std::string database_folder = TRELLIS_PREFIX "/share/trellis/database";

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
    options.add_options()("db", po::value<std::string>(), "Trellis database folder location");
    options.add_options()("idcode", po::value<std::string>(), "IDCODE to override in bitstream");
    po::positional_options_description pos;
    options.add_options()("input", po::value<std::string>()->required(), "input bitstream file");
    pos.add("input", 1);
    options.add_options()("textcfg", po::value<std::string>()->required(), "output textual configuration");
    pos.add("textcfg", 1);

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
        cerr << "ecpunpack: ECP5 bitstream to text config converter" << endl;
        cerr << endl;
        cerr << "Copyright (C) 2018 David Shah <david@symbioticeda.com>" << endl;
        cerr << endl;
        cerr << options << endl;
        return vm.count("help") ? 0 : 1;
    }

    ifstream bit_file(vm["input"].as<string>(), ios::binary);
    if (!bit_file) {
        cerr << "Failed to open input file" << endl;
        return 1;
    }

    if (vm.count("db")) {
        database_folder = vm["db"].as<string>();
    }

    if (vm.count("idcode")) {
        string idcode_str = vm["idcode"].as<string>();
        uint32_t idcode_val;
        idcode_val = uint32_t(strtoul(idcode_str.c_str(), nullptr, 0));
        if (idcode_val == 0) {
            cerr << "Invalid idcode: " << idcode_str << endl;
            return 1;
        }
        idcode = idcode_val;
    }

    try {
        load_database(database_folder);
    } catch (runtime_error &e) {
        cerr << "Failed to load Trellis database: " << e.what() << endl;
        return 1;
    }

    try {
        Chip c = Bitstream::read_bit(bit_file).deserialise_chip(idcode);
        ChipConfig cc = ChipConfig::from_chip(c);
        ofstream out_file(vm["textcfg"].as<string>());
        if (!out_file) {
            cerr << "Failed to open output file" << endl;
            return 1;
        }
        out_file << cc.to_string();
        return 0;
    } catch (runtime_error &e) {
        cerr << "Failed to process input bitstream: " << e.what() << endl;
        return 1;
    }

}
