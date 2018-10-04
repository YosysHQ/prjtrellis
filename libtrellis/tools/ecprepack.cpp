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

    std::string database_folder = TRELLIS_PREFIX "/share/trellis/database";

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
    options.add_options()("db", po::value<std::string>(), "Trellis database folder location");
    po::positional_options_description pos;
    options.add_options()("input", po::value<std::string>()->required(), "input bitstream file");
    pos.add("input", 1);
    options.add_options()("id", po::value<std::string>(), "chip ID to set in output bitstream");
    pos.add("id", 1);
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
        cerr << "ecprepack: ECP5 bitstream repacker" << endl;
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

    try {
        load_database(database_folder);
    } catch (runtime_error &e) {
        cerr << "Failed to load Trellis database: " << e.what() << endl;
        return 1;
    }

    try {
        Chip c = Bitstream::read_bit(bit_file).deserialise_chip();
        ofstream out_bit_file(vm["output"].as<string>(), ios::binary);
        if (!out_bit_file) {
           cerr << "Failed to open output file" << endl;
        }
        if(vm.count("id"))
          c.info.idcode = strtoul((vm["id"].as<string>()).c_str(), NULL, 0);
        Bitstream::serialise_chip(c).write_bit(out_bit_file);
        return 0;
    } catch (runtime_error &e) {
        cerr << "Failed to process input bitstream: " << e.what() << endl;
        return 1;
    }

}
