


/* I was unable to find good information on how the PLL dividers work
in the ECP5 PLL Design and Usage Guide, so I ran several frequencies
through Lattice's clarity designer, and was surprised with what I
found:
| Input | Output | refclk | feedback | output | fvco |
|    12 |     48 |      1 |        4 |     12 |  576 |
|    12 |     60 |      1 |        5 |     10 |  600 |
|    20 |     30 |      2 |        3 |     20 |  600 |
|    45 |     30 |      3 |        2 |     20 |  600 |
|   100 |    400 |      1 |        4 |      1 |  400 |
|   200 |    400 |      1 |        2 |      2 |  800 |
|    50 |    400 |      1 |        8 |      2 |  800 |
|    70 |     40 |      7 |        4 |     15 |  600 |
|    12 |     36 |      1 |        3 |     18 |  648 |
|    12 |     96 |      1 |        8 |      6 |  576 |
|    90 |     40 |      9 |        4 |     15 |  600 |
|    90 |     50 |      9 |        5 |     13 |  650 |
|    43 |     86 |      1 |        2 |      7 |  602 |

it appears that
f_pfd = f_in/refclk
f_vco = f_pfd * feedback * output
f_out = f_vco / output
 */

#define INPUT_MIN 8.0f
#define INPUT_MAX 400.0f
#define OUTPUT_MIN 10.0f
#define OUTPUT_MAX 400.0f
#define PFD_MIN 3.125f
#define PFD_MAX 400.0f
#define VCO_MIN 400.0f
#define VCO_MAX 800.0f
#include <iostream>
#include <boost/program_options.hpp>
using namespace std;



int main(int argc, char** argv){
  namespace po = boost::program_options;
  po::options_description options("Allowed options");

  options.add_options()("help,h", "show help");
  options.add_options()("input,i", po::value<float>()->required(), "Input frequency in MHz");
  options.add_options()("output,o", po::value<float>()->required(), "Output frequency in MHz");

  po::variables_map vm;
  po::parsed_options parsed = po::command_line_parser(argc, argv).options(options).run();
  po::store(parsed, vm);
  po::notify(vm);

  if(vm.count("help")){
    cerr << "Project Trellis - Open Source Tools for ECP5 FPGAs" << endl;
    cerr << "ecpunpack: ECP5 bitstream to text config converter" << endl;
    cerr << endl;
    cerr << "Copyright (C) 2018 David Shah <david@symbioticeda.com>" << endl;
    cerr << endl;
    cerr << options << endl;
  }
  float inputf = vm["input"].as<float>();
  float outputf = vm["output"].as<float>();
  if(inputf < INPUT_MIN || inputf > INPUT_MAX){
    fprintf(stderr, "Input frequency %.3fMHz not in range (%.3fMHz, %.3fMHz)\n",
	    inputf, INPUT_MIN, INPUT_MAX);
    return 1;
  }
  if(outputf < OUTPUT_MIN || outputf > OUTPUT_MAX){
    fprintf(stderr, "Output frequency %.3fMHz not in range (%.3fMHz, %.3fMHz)\n",
	    outputf, OUTPUT_MIN, OUTPUT_MAX);
    return 1;
  }

}
