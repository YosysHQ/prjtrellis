


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

enum class pll_mode{
  SIMPLE,
  HIGHRES
};

struct secondary_params{
  bool enabled;
  int div;
  int cphase;
  int fphase;

  float freq;
  float phase;
};
  

struct pll_params{
  pll_mode mode;
  int refclk_div;
  int feedback_div;
  int output_div;
  int primary_cphase;

  secondary_params secondary[3];

  float fout;
  float fvco;

  pll_params() :mode(pll_mode::SIMPLE) {
    for(int i=0;i<3;i++){
      secondary[i].enabled = false;
      primary_cphase = 9;
    }
  }
};

pll_params calc_pll_params(float input, float output);
pll_params calc_pll_params_highres(float input, float output);
void generate_secondary_output(pll_params &params, int channel, float frequency, float phase);
void write_pll_config(pll_params params, const char* name, ofstream& file);

int main(int argc, char** argv){
  namespace po = boost::program_options;
  po::options_description options("Allowed options");

  options.add_options()("help,h", "show help");
  options.add_options()("input,i", po::value<float>(), "Input frequency in MHz");
  options.add_options()("output,o", po::value<float>(), "Output frequency in MHz");
  options.add_options()("s1", po::value<float>(), "Secondary Output frequency in MHz");
  options.add_options()("p1", po::value<float>()->default_value(0), "Secondary Output phase in degrees");
  options.add_options()("s2", po::value<float>(), "Secondary Output(2) frequency in MHz");
  options.add_options()("p2", po::value<float>()->default_value(0), "Secondary Output(2) phase in degrees");
  options.add_options()("s3", po::value<float>(), "Secondary Output(3) frequency in MHz");
  options.add_options()("p3", po::value<float>()->default_value(0), "Secondary Output(3) phase in degrees");
  options.add_options()("file,f", po::value<string>(), "Output to file");
  options.add_options()("highres", "Use secondary PLL output for higher frequency resolution");

  po::variables_map vm;
  po::parsed_options parsed = po::command_line_parser(argc, argv).options(options).run();
  po::store(parsed, vm);
  po::notify(vm);

  if(vm.count("help")){
    cerr << "Project Trellis - Open Source Tools for ECP5 FPGAs" << endl;
    cerr << "ecppll: ECP5 PLL Configuration Calculator" << endl;
    cerr << endl;
    cerr << "This tool is experimental! Use at your own risk!" << endl;
    cerr << endl;
    cerr << "Copyright (C) 2018-2019 David Shah <david@symbioticeda.com>" << endl;
    cerr << endl;
    cerr << options << endl;
    return 1;
  }
  if(vm.count("input") != 1 || vm.count("output") != 1){
    cerr << "Error: missing input or output frequency!\n";
    return 1;
  }
  float inputf = vm["input"].as<float>();
  float outputf = vm["output"].as<float>();
  if(inputf < INPUT_MIN || inputf > INPUT_MAX){
    cerr << "Warning: Input frequency " << inputf << "MHz not in range (" << INPUT_MIN << "MHz, " << INPUT_MAX << "MHz)\n";
  }
  if(outputf < OUTPUT_MIN || outputf > OUTPUT_MAX){
    cerr << "Warning: Output frequency " << outputf << "MHz not in range (" << OUTPUT_MIN << "MHz, " << OUTPUT_MAX << "MHz)\n";
  }
  pll_params params;
  if(vm.count("highres")){
    if(vm.count("s1") > 0){
      cerr << "Cannot specify secondary frequency in highres mode\n";
    }
    params = calc_pll_params_highres(inputf, outputf);
  }
  else{
    params = calc_pll_params(inputf, outputf);
    if(vm.count("s1"))
      generate_secondary_output(params, 0, vm["s1"].as<float>(), vm["p1"].as<float>());
    if(vm.count("s2"))
      generate_secondary_output(params, 1, vm["s2"].as<float>(), vm["p2"].as<float>());
    if(vm.count("s3"))
      generate_secondary_output(params, 2, vm["s3"].as<float>(), vm["p3"].as<float>());
      
  }

  cout << "Pll parameters:" << endl;
  cout << "Refclk divisor: " << params.refclk_div << endl;
  cout << "Feedback divisor: " << params.feedback_div << endl;
  cout << "Output divisor: " << params.output_div << endl;
  if(params.secondary[0].enabled){
    cout << "Secondary divisor: " << params.secondary[0].div << endl;
    cout << "Secondary freq: " << params.secondary[0].freq << endl;
    cout << "Secondary phase shift: " << params.secondary[0].phase << endl;
  }
  if(params.secondary[1].enabled){
    cout << "Secondary(2) divisor: " << params.secondary[1].div << endl;
    cout << "Secondary(2) freq: " << params.secondary[1].freq << endl;
    cout << "Secondary(2) phase shift: " << params.secondary[1].phase << endl;
  }
  if(params.secondary[2].enabled){
    cout << "Secondary(3) divisor: " << params.secondary[2].div << endl;
    cout << "Secondary(3) freq: " << params.secondary[2].freq << endl;
    cout << "Secondary(3) phase shift: " << params.secondary[2].phase << endl;
  }
  cout << "VCO frequency: " << params.fvco << endl;
  cout << "Output frequency: " << params.fout << endl;
  if(vm.count("file")){
    ofstream f;

    f.open(vm["file"].as<string>().c_str());

    
    write_pll_config(params, "pll", f);

    f.close();
  }

}

pll_params calc_pll_params(float input, float output){
  float error = std::numeric_limits<float>::max();
  pll_params params;
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
	  
	  // shift the primary by 180 degrees. Lattice seems to do this
	  float ns_phase = 1/(fout * 1e6) * 0.5;
	  params.primary_cphase = ns_phase * (fvco * 1e6);

	}

      }
    }
  }
  return params;
}

pll_params calc_pll_params_highres(float input, float output){
  float error = std::numeric_limits<float>::max();
  pll_params params;
  for(int input_div=1;input_div <= 128; input_div++){

    float fpfd = input / (float)input_div;
    if(fpfd < PFD_MIN || fpfd > PFD_MAX)
      continue;
    for(int feedback_div=1;feedback_div <= 80; feedback_div++){
      for(int output_div=1;output_div <= 128; output_div++){
	float fvco = fpfd * (float)feedback_div * (float) output_div;
	
	if(fvco < VCO_MIN || fvco > VCO_MAX)
	  continue;
	float ffeedback = fvco / (float) output_div;
	if(ffeedback < OUTPUT_MIN || ffeedback > OUTPUT_MAX)
	  continue;
	for(int secondary_div = 1; secondary_div <= 128; secondary_div++){
	  float fout = fvco / (float) secondary_div;
	  if(fabsf(fout - output) < error ||
	     (fabsf(fout-output) == error && fabsf(fvco - 600) < fabsf(params.fvco - 600))){
	    error = fabsf(fout-output);
	    params.mode = pll_mode::HIGHRES;
	    params.refclk_div = input_div;
	    params.feedback_div = feedback_div;
	    params.output_div = output_div;
	    params.secondary[0].div = secondary_div;
	    params.secondary[0].enabled = true;
	    params.secondary[0].freq = fout;
	    params.fout = fout;
	    params.fvco = fvco;

	  }
	}

      }
    }
  }
  return params;
}


void generate_secondary_output(pll_params &params, int channel, float frequency, float phase){
  int div = params.fvco/frequency;
  float freq = params.fvco/div;
  cout << "sdiv " << div << endl;

  float ns_shift = 1/(freq * 1e6) * phase /  360.0;
  float phase_count = ns_shift * (params.fvco * 1e6);
  int cphase = (int) phase_count;
  int fphase = (int) ((phase_count - cphase) * 8);

  float ns_actual = 1/(params.fvco * 1e6) * (cphase + fphase/8.0);
  float phase_shift = 360 * ns_actual/ (1/(freq * 1e6));
  

  params.secondary[channel].enabled = true;
  params.secondary[channel].div = div;
  params.secondary[channel].freq = freq;
  params.secondary[channel].phase = phase_shift;
  params.secondary[channel].cphase = cphase + params.primary_cphase;
  params.secondary[channel].fphase = fphase;
  
  

}

void write_pll_config(pll_params params, const char* name,  ofstream& file){
  file << "module " << name << "(input clki, \n";
  for(int i=0;i<3;i++){
    if(!(i==0 && params.mode == pll_mode::HIGHRES) && params.secondary[i].enabled){
      file << "    output clks" << i+1 <<",\n";
    }
  }
  file << "    output locked,\n";
  file << "    output clko\n";
  file << ");\n";
  file << "wire clkfb;\n";
  file << "wire clkos;\n";
  file << "wire clkop;\n";
  file << "(* ICP_CURRENT=\"12\" *) (* LPF_RESISTOR=\"8\" *) (* MFG_ENABLE_FILTEROPAMP=\"1\" *) (* MFG_GMCREF_SEL=\"2\" *)\n";
  file << "EHXPLLL #(\n";
  file << "        .PLLRST_ENA(\"DISABLED\"),\n";
  file << "        .INTFB_WAKE(\"DISABLED\"),\n";
  file << "        .STDBY_ENABLE(\"DISABLED\"),\n";
  file << "        .DPHASE_SOURCE(\"DISABLED\"),\n";
  file << "        .CLKOP_FPHASE(0),\n";
  file << "        .CLKOP_CPHASE(" << params.primary_cphase << "),\n";
  file << "        .OUTDIVIDER_MUXA(\"DIVA\"),\n";
  file << "        .CLKOP_ENABLE(\"ENABLED\"),\n";
  file << "        .CLKOP_DIV(" << params.output_div << "),\n";
  if(params.secondary[0].enabled){
    file << "        .CLKOS_ENABLE(\"ENABLED\"),\n";
    file << "        .CLKOS_DIV(" << params.secondary[0].div << "),\n";
    file << "        .CLKOS_CPHASE(" << params.secondary[0].cphase << "),\n";
    file << "        .CLKOS_FPHASE(" << params.secondary[0].fphase << "),\n";
  }
  if(params.secondary[1].enabled){
    file << "        .CLKOS2_ENABLE(\"ENABLED\"),\n";
    file << "        .CLKOS2_DIV(" << params.secondary[1].div << "),\n";
    file << "        .CLKOS2_CPHASE(" << params.secondary[1].cphase << "),\n";
    file << "        .CLKOS2_FPHASE(" << params.secondary[1].fphase << "),\n";
  }
  if(params.secondary[2].enabled){
    file << "        .CLKOS3_ENABLE(\"ENABLED\"),\n";
    file << "        .CLKOS3_DIV(" << params.secondary[2].div << "),\n";
    file << "        .CLKOS3_CPHASE(" << params.secondary[2].cphase << "),\n";
    file << "        .CLKOS3_FPHASE(" << params.secondary[2].fphase << "),\n";
  }
  file << "        .CLKFB_DIV(" << params.feedback_div << "),\n";
  file << "        .CLKI_DIV(" << params.refclk_div <<"),\n";
  file << "        .FEEDBK_PATH(\"INT_OP\")\n";
  file << "    ) pll_i (\n";
  file << "        .CLKI(clki),\n";
  file << "        .CLKFB(clkfb),\n";
  file << "        .CLKINTFB(clkfb),\n";
  file << "        .CLKOP(clkop),\n";
  if(params.secondary[0].enabled){
    if(params.mode == pll_mode::HIGHRES)
      file << "        .CLKOS(clkos),\n";
    else
      file << "        .CLKOS(clks1),\n";

  }
  if(params.secondary[1].enabled){
    file << "        .CLKOS2(clks2),\n";
  }
  if(params.secondary[2].enabled){
    file << "        .CLKOS3(clks3),\n";
  }
  file << "        .RST(1'b0),\n";
  file << "        .STDBY(1'b0),\n";
  file << "        .PHASESEL0(1'b0),\n";
  file << "        .PHASESEL1(1'b0),\n";
  file << "        .PHASEDIR(1'b0),\n";
  file << "        .PHASESTEP(1'b0),\n";
  file << "        .PLLWAKESYNC(1'b0),\n";
  file << "        .ENCLKOP(1'b0),\n";
  file << "        .LOCK(locked)\n";
  file << "	);\n";
  if(params.mode == pll_mode::SIMPLE){
    file << "assign clko = clkop;\n";
  }
  else {
    file << "assign clko = clkos;\n";
  }
  file << "endmodule\n";

}
