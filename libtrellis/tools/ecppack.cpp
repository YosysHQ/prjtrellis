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
    options.add_options()("usercode", po::value<uint32_t>(), "USERCODE to set in bitstream");
    po::positional_options_description pos;
    options.add_options()("input", po::value<std::string>()->required(), "input textual configuration");
    pos.add("input", 1);
    options.add_options()("bit", po::value<std::string>()->required(), "output bitstream file");
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

    string textcfg((std::istreambuf_iterator<char>(config_file)), std::istreambuf_iterator<char>());

    ChipConfig cc;
    try {
        cc = ChipConfig::from_string(textcfg);
    } catch (runtime_error &e) {
        cerr << "Failed to process input config: " << e.what() << endl;
        return 1;
    }

    Chip c = cc.to_chip();

    ofstream bit_file(vm["bit"].as<string>(), ios::binary);
    if (!bit_file) {
        cerr << "Failed to open output file" << endl;
    }
    Bitstream::serialise_chip(c).write_bit(bit_file);
    return 0;
}
