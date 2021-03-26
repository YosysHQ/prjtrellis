//
//  Copyright (C) 2016  Clifford Wolf <clifford@clifford.at>
//  Copyright (C) 2019  Sylvain Munaut <tnt@246tNt.com>
//
//  Permission to use, copy, modify, and/or distribute this software for any
//  purpose with or without fee is hereby granted, provided that the above
//  copyright notice and this permission notice appear in all copies.
//
//  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
//  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
//  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
//  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
//  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
//  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
//  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>
#ifdef _WIN32
#define NOMINMAX
#include "windows.h"
#undef NOMINMAX
#else
#include <unistd.h>
#include <sys/time.h>
#endif

#include <map>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>

#include <boost/program_options.hpp>

#include "ChipConfig.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "DatabasePath.hpp"
#include "wasmexcept.hpp"

using std::map;
using std::pair;
using std::vector;
using std::string;
using std::ifstream;
using std::getline;

uint64_t x;
uint64_t xorshift64star(void) {
    x ^= x >> 12; // a
    x ^= x << 25; // b
    x ^= x >> 27; // c
    return x * UINT64_C(2685821657736338717);
}

void push_back_bitvector(vector<vector<bool>> &hexfile, const vector<int> &digits)
{
    if (digits.empty())
        return;

    hexfile.push_back(vector<bool>(digits.size() * 4));

    for (int i = 0; i < int(digits.size()) * 4; i++)
        if ((digits.at(digits.size() - i/4 -1) & (1 << (i%4))) != 0)
            hexfile.back().at(i) = true;
}

void parse_hexfile_line(const char *filename, int linenr, vector<vector<bool>> &hexfile, string &line, int &address)
{
    vector<int> digits;
    bool reading_address = false;
    
    for (char c : line) {
        if ('0' <= c && c <= '9')
            digits.push_back(c - '0');
        else if ('a' <= c && c <= 'f')
            digits.push_back(10 + c - 'a');
        else if ('A' <= c && c <= 'F')
            digits.push_back(10 + c - 'A');
        else if ('x' == c || 'X' == c ||
             'z' == c || 'Z' == c)
            digits.push_back(0);
        else if ('_' == c)
            ;
	else if ('@' == c) {
	    if (reading_address || !digits.empty())
		goto error;
	    else
		reading_address = true;
        } else if (' ' == c || '\t' == c || '\r' == c) {
	    if (reading_address) {
		int file_address = 0;
		for (int i = 0; i < int(digits.size()); i++ ) {
		    file_address <<= 4;
		    file_address |= digits.at(i);
		}
		if (file_address != address) {
		    fprintf(stderr, "Non-contiguous address (expected @%X) at line %d of %s: %s\n", address, linenr, filename, line.c_str());
		    exit(1);
		}
	    } else {
		push_back_bitvector(hexfile, digits);
		if( !digits.empty() )
		    address++;
	    }
	    digits.clear();
	    reading_address = false;
        } else goto error;
    }

    push_back_bitvector(hexfile, digits);

    return;

error:
    fprintf(stderr, "Can't parse line %d of %s: %s\n", linenr, filename, line.c_str());
    exit(1);
}

int main(int argc, char **argv)
{
    bool verbose = false;
    namespace po = boost::program_options;

    std::string database_folder = get_database_path();;

    po::options_description options("Allowed options");

    po::options_description options_any("Generic options");
    options_any.add_options()("help,h", "show help");
    options_any.add_options()("verbose,v", "verbose output");

    po::options_description options_init("Initialize options");
    options_init.add_options()("input,i", po::value<std::string>(), "input configuration file");
    options_init.add_options()("output,o", po::value<std::string>(), "output configuration file");
    options_init.add_options()("from,f", po::value<std::string>(), "original content hex file");
    options_init.add_options()("to,t", po::value<std::string>(), "new content hex file");

    po::options_description options_gen("Generate options");
    options_gen.add_options()("generate,g", po::value<std::string>(), "Generate random hex of given geometry into given file");
    options_gen.add_options()("seed,s", po::value<int>(), "seed random generator with fixed value");
    options_gen.add_options()("width,w", po::value<int>(), "width of the BRAM content (in bits)");
    options_gen.add_options()("depth,d", po::value<int>(), "idepth of the BRAM content (in # of words)");

    options.add(options_any).add(options_init).add(options_gen);

    po::variables_map vm;
    try {
        po::parsed_options parsed = po::command_line_parser(argc, argv).options(options).run();
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
        cerr << argv[0] << ": ECP5 BRAM content initialization tool" << endl;
        cerr << endl;
        cerr << "Copyright (C) 2019  Sylvain Munaut <tnt@246tNt.com>" << endl;
        cerr << "Copyright (C) 2016  Clifford Wolf <clifford@clifford.at>" << endl;
        cerr << endl;
        cerr << options << endl;
        return vm.count("help") ? 0 : 1;
    }

    if (vm.count("verbose"))
        verbose = true;

    if (vm.count("generate"))
    {
        if (!vm.count("width") || !vm.count("depth"))
            goto help;

        int width = vm.at("width").as<int>();
        int depth = vm.at("depth").as<int>();

        if (width <= 0 || width % 4 != 0) {
            fprintf(stderr, "Hexfile width (%d bits) is not divisible by 4 or nonpositive!\n", width);
            return 1;
        }

        if (depth <= 0 || depth % 512 != 0) {
            fprintf(stderr, "Hexfile number of words (%d) is not divisible by 512 or nonpositive!\n", depth);
            return 1;
        }

        // If -s is provided: seed with the given value.
        // If -s is not provided: seed with the PID and current time, which are unlikely 
        // to repeat simultaneously.
        uint32_t seed_nr;
        if (vm.count("seed")) {
            seed_nr = vm.at("seed").as<int>();

            if (verbose)
                fprintf(stderr, "Seed: %d\n", seed_nr);
        } else {
#if defined(__wasm)
            seed_nr = 0;
#elif defined(_WIN32)
            seed_nr = GetCurrentProcessId();
#else
            seed_nr = getpid();
#endif
        }

        x  = uint64_t(seed_nr) << 32;
        x ^= uint64_t(seed_nr) << 20;
        x ^= uint64_t(seed_nr);

        x ^= uint64_t(depth) << 16;
        x ^= uint64_t(width) << 10;

        xorshift64star();
        xorshift64star();
        xorshift64star();

        if (!vm.count("seed")) {
#ifdef _WIN32
            SYSTEMTIME system_time;
            FILETIME file_time;
            uint64_t time;
            GetSystemTime(&system_time);
            SystemTimeToFileTime(&system_time, &file_time);
            x ^= uint64_t(file_time.dwLowDateTime);
            x ^= uint64_t(file_time.dwHighDateTime) << 32;
#else
            struct timeval tv;
            gettimeofday(&tv, NULL);
            x ^= uint64_t(tv.tv_sec) << 20;
            x ^= uint64_t(tv.tv_usec);
#endif
        }

        xorshift64star();
        xorshift64star();
        xorshift64star();

        ofstream romfile(vm.at("generate").as<std::string>());

        for (int i = 0; i < depth; i++) {
            for (int j = 0; j < width / 4; j++) {
                int digit = xorshift64star() & 15;
                romfile << "0123456789abcdef"[digit];
            }
            romfile << std::endl;
        }

        return 0;
    }

    if (!vm.count("input") || !vm.count("output") || !vm.count("from") || !vm.count("to"))
        goto help;

    // -------------------------------------------------------
    // Load from_hexfile and to_hexfile

    const char *from_hexfile_n = vm.at("from").as<std::string>().c_str();
    ifstream from_hexfile_f(from_hexfile_n);
    vector<vector<bool>> from_hexfile;

    const char *to_hexfile_n = vm.at("to").as<std::string>().c_str();
    ifstream to_hexfile_f(to_hexfile_n);
    vector<vector<bool>> to_hexfile;

    string line;
    
    for (int i = 1, address = 0; getline(from_hexfile_f, line); i++)
        parse_hexfile_line(from_hexfile_n, i, from_hexfile, line, address);

    for (int i = 1, address = 0; getline(to_hexfile_f, line); i++)
        parse_hexfile_line(to_hexfile_n, i, to_hexfile, line, address);

    if (to_hexfile.size() > 0 && from_hexfile.size() > to_hexfile.size()) {
        if (verbose)
            fprintf(stderr, "Padding to_hexfile from %d words to %d\n",
                int(to_hexfile.size()), int(from_hexfile.size()));
        do
            to_hexfile.push_back(vector<bool>(to_hexfile.at(0).size()));
        while (from_hexfile.size() > to_hexfile.size());
    }

    if (from_hexfile.size() != to_hexfile.size()) {
        fprintf(stderr, "Hexfiles have different number of words! (%d vs. %d)\n", int(from_hexfile.size()), int(to_hexfile.size()));
        return 1;
    }

    if (from_hexfile.size() % 512 != 0) {
        fprintf(stderr, "Hexfile number of words (%d) is not divisible by 512!\n", int(from_hexfile.size()));
        return 1;
    }

    for (size_t i = 1; i < from_hexfile.size(); i++)
        if (from_hexfile.at(i-1).size() != from_hexfile.at(i).size()) {
            fprintf(stderr, "Inconsistent word width at line %d of %s!\n", int(i), from_hexfile_n);
            return 1;
        }

    for (size_t i = 1; i < to_hexfile.size(); i++) {
        while (to_hexfile.at(i-1).size() > to_hexfile.at(i).size())
            to_hexfile.at(i).push_back(false);
        if (to_hexfile.at(i-1).size() != to_hexfile.at(i).size()) {
            fprintf(stderr, "Inconsistent word width at line %d of %s!\n", int(i+1), to_hexfile_n);
            return 1;
        }
    }

    if (from_hexfile.size() == 0 || from_hexfile.at(0).size() == 0) {
        fprintf(stderr, "Empty from/to hexfiles!\n");
        return 1;
    }

    if (verbose)
        fprintf(stderr, "Loaded pattern for %d bits wide and %d words deep memory.\n", int(from_hexfile.at(0).size()), int(from_hexfile.size()));


    // -------------------------------------------------------
    // Create bitslices from pattern data

    map<vector<bool>, pair<vector<bool>, int>> pattern;

    for (int i = 0; i < int(from_hexfile.at(0).size()); i++)
    {
        vector<bool> pattern_from, pattern_to;

        for (int j = 0; j < int(from_hexfile.size()); j++)
        {
            pattern_from.push_back(from_hexfile.at(j).at(i));
            pattern_to.push_back(to_hexfile.at(j).at(i));

            if (pattern_from.size() == 512) {
                if (pattern.count(pattern_from)) {
                    fprintf(stderr, "Conflicting from pattern for bit slice from_hexfile[%d:%d][%d]!\n", j, j-255, i);
                    return 1;
                }
                pattern[pattern_from] = std::make_pair(pattern_to, 0);
                pattern_from.clear(), pattern_to.clear();
            }
        }

        assert(pattern_from.empty());
        assert(pattern_to.empty());
    }

    if (verbose)
        fprintf(stderr, "Extracted %d bit slices from from/to hexfile data.\n", int(pattern.size()));


    // -------------------------------------------------------
    // Load database and config

    ifstream config_file(vm.at("input").as<string>());

    try {
        Trellis::load_database(database_folder);
    } catch (runtime_error &e) {
        cerr << "Failed to load Trellis database: " << e.what() << endl;
        return 1;
    }

    string textcfg((std::istreambuf_iterator<char>(config_file)), std::istreambuf_iterator<char>());

    Trellis::ChipConfig cc;
    try {
        cc = Trellis::ChipConfig::from_string(textcfg);
    } catch (runtime_error &e) {
        cerr << "Failed to process input config: " << e.what() << endl;
        return 1;
    }

    // -------------------------------------------------------
    // Replace bram data

    int max_replace_cnt = 0;

    for (auto &bram_it : cc.bram_data)
    {
        auto &bram_data = bram_it.second;

        const int W[] =  {  1,  2,  4,  9, 18, 36 };
        const int NW[] = {  8,  8,  8,  9,  9,  9 };
        const int B[]  = { 32, 32, 32, 36, 36, 36 };

        for (int i = 0; i < 6; i++)
        {
            for (int j = 0; j < B[i]; j++)
            {
                vector<bool> from_bitslice;

                for (int k = 0; k < 512; k++)
                {
                    int bn = (k * W[i]) + (j % W[i]) + ((j/W[i]) * 512 * W[i]);
                    int word  = bn / NW[i];
                    int bit   = bn % NW[i];

                    from_bitslice.push_back((bram_data.at(word) & (1 << bit)) != 0);
                }

                auto p = pattern.find(from_bitslice);
                if (p != pattern.end())
                {
                    auto &to_bitslice = p->second.first;

                    for (int k = 0; k < 512; k++)
                    {
                        int bn = (k * W[i]) + (j % W[i]) + ((j/W[i]) * 512 * W[i]);
                        int word  = bn / NW[i];
                        int bit   = bn % NW[i];

                        if (to_bitslice.at(k))
                            bram_data.at(word) |=  (1 << bit);
                        else
                            bram_data.at(word) &= ~(1 << bit);
                    }

                    max_replace_cnt = std::max(++p->second.second, max_replace_cnt);
                }
            }
        }
    }

    // -------------------------------------------------------
    // Save the new config

    ofstream new_config_file(vm.at("output").as<std::string>());
    new_config_file << cc.to_string();

    return 0;
}
