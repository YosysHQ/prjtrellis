


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
#include <limits>
#include <fstream>
#include <boost/program_options.hpp>
using namespace std;


struct pll_params{
  int refclk_div;
  int feedback_div;
  int output_div;

  float fout;
  float fvco;
};

pll_params calc_pll_params(float input, float output);
void write_pll_config(pll_params params, const char* name, ofstream& file);

int main(int argc, char** argv){
  namespace po = boost::program_options;
  po::options_description options("Allowed options");

  options.add_options()("help,h", "show help");
  options.add_options()("input,i", po::value<float>()->required(), "Input frequency in MHz");
  options.add_options()("output,o", po::value<float>()->required(), "Output frequency in MHz");
  options.add_options()("file,f", po::value<string>(), "Output to file");

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
  pll_params params = calc_pll_params(inputf, outputf);

  fprintf(stdout, "Pll parameters:\n");
  fprintf(stdout, "Refclk divisor: %d\n", params.refclk_div);
  fprintf(stdout, "Feedback divisor: %d\n", params.feedback_div);
  fprintf(stdout, "Output divisor: %d\n", params.output_div);
  fprintf(stdout, "VCO frequency: %f\n", params.fvco);
  fprintf(stdout, "Output frequency: %f\n", params.fout);
  if(vm.count("file")){
    ofstream f;

    // if(vm["file"].as<string>() == "-")
    //   f = stdout;
    // else
    f.open(vm["file"].as<string>().c_str());

    
    write_pll_config(params, "pll", f);

    f.close();
  }

}

pll_params calc_pll_params(float input, float output){
  float error = std::numeric_limits<float>::max();
  pll_params params = {0};
  for(int input_div=1;input_div <= 128; input_div++){

    float fpfd = input / (float)input_div;
    if(fpfd < PFD_MIN || fpfd > PFD_MAX)
      continue;
    for(int feedback_div=1;feedback_div <= 80; feedback_div++){
      for(int output_div=1;output_div <= 128; output_div++){
	float fvco = fpfd * (float)feedback_div * (float) output_div;
	
	if(fvco < VCO_MIN || fvco > VCO_MAX)
	  continue;

	float fout = fvco / (float) output_div;
	if(fabsf(fout - output) < error ||
	   (fabsf(fout-output) == error && fabsf(fvco - 600) < fabsf(params.fvco - 600))){
	  error = fabsf(fout-output);
	  params.refclk_div = input_div;
	  params.feedback_div = feedback_div;
	  params.output_div = output_div;
	  params.fout = fout;
	  params.fvco = fvco;

	}

      }
    }
  }
  return params;
}

void write_pll_config(pll_params params, const char* name,  ofstream& file){
  file << "module " << name << "(input clki, output clko);\n";
  file << "(* ICP_CURRENT=\"12\" *) (* LPF_RESISTOR=\"8\" *) (* MFG_ENABLE_FILTEROPAMP=\"1\" *) (* MFG_GMCREF_SEL=\"2\" *)\n";
  file << "EHXPLLL #(\n";
  file << "        .PLLRST_ENA(\"DISABLED\"),\n";
  file << "        .INTFB_WAKE(\"DISABLED\"),\n";
  file << "        .STDBY_ENABLE(\"DISABLED\"),\n";
  file << "        .DPHASE_SOURCE(\"DISABLED\"),\n";
  file << "        .CLKOP_FPHASE(0),\n";
  file << "        .CLKOP_CPHASE(11),\n";
  file << "        .OUTDIVIDER_MUXA(\"DIVA\"),\n";
  file << "        .CLKOP_ENABLE(\"ENABLED\"),\n";
  file << "        .CLKOP_DIV(" << params.output_div << "),\n";
  file << "        .CLKFB_DIV(" << params.feedback_div << "),\n";
  file << "        .CLKI_DIV(" << params.refclk_div <<"),\n";
  file << "        .FEEDBK_PATH(\"CLKOP\")\n";
  file << "    ) pll_i (\n";
  file << "        .CLKI(clki),\n";
  file << "        .CLKFB(clko),\n";
  file << "        .CLKOP(clko),\n";
  file << "        .RST(1'b0),\n";
  file << "        .STDBY(1'b0),\n";
  file << "        .PHASESEL0(1'b0),\n";
  file << "        .PHASESEL1(1'b0),\n";
  file << "        .PHASEDIR(1'b0),\n";
  file << "        .PHASESTEP(1'b0),\n";
  file << "        .PLLWAKESYNC(1'b0),\n";
  file << "        .ENCLKOP(1'b0),\n";
  file << "	);\n";
  file << "endmodule\n";

}
