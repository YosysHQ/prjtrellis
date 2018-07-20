#include "ChipConfig.hpp"
#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include <iostream>
#include <boost/program_options.hpp>
#include <stdexcept>
#include <streambuf>
#include <fstream>

using namespace std;

int main(int argc, char *argv[])
{
    using namespace Trellis;
    namespace po = boost::program_options;

    load_database(TRELLIS_PREFIX "/share/trellis/database/");

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
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

    try {
        Chip c = Bitstream::read_bit(bit_file).deserialise_chip();
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
