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
#include <string>
#include <boost/program_options.hpp>
#include "version.hpp"
#include "wasmexcept.hpp"
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
  string name;

  float freq;
  float phase;
};

struct pll_params{
  pll_mode mode;
  int refclk_div;
  int feedback_div;
  int output_div;
  int primary_cphase;
  string clkin_name;
  string clkout0_name;
  int dynamic;
  int reset, standby;
  int feedback_clkout, internal_feedback, internal_feedback_wake;
  string feedback_name[4], feedback_wname[4];


  float clkin_frequency;

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

void calc_pll_params(pll_params &params, float input, float output);
void calc_pll_params_highres(pll_params &params, float input, float output);
void generate_secondary_output(pll_params &params, int channel, string name, float frequency, float phase);
void write_pll_config(const pll_params & params, const string &name, ofstream& file);

int main(int argc, char** argv){
  namespace po = boost::program_options;
  po::options_description options("Allowed options");

  options.add_options()("help,h", "show help");
  options.add_options()("module,n", po::value<string>(), "module name");
  options.add_options()("clkin_name", po::value<string>(), "Input signal name");
  options.add_options()("clkin,i", po::value<float>(), "Input frequency in MHz");
  options.add_options()("clkout0_name", po::value<string>(), "Primary Output(0) signal name");
  options.add_options()("clkout0,o", po::value<float>(), "Primary Output(0) frequency in MHz");
  options.add_options()("clkout1_name", po::value<string>(), "Secondary Output(1) signal name");
  options.add_options()("clkout1", po::value<float>(), "Secondary Output(1) frequency in MHz");
  options.add_options()("phase1", po::value<float>()->default_value(0), "Secondary Output(1) phase in degrees");
  options.add_options()("clkout2_name", po::value<string>(), "Secondary Output(2) signal name");
  options.add_options()("clkout2", po::value<float>(), "Secondary Output(2) frequency in MHz");
  options.add_options()("phase2", po::value<float>()->default_value(0), "Secondary Output(2) phase in degrees");
  options.add_options()("clkout3_name", po::value<string>(), "Secondary Output(3) signal name");
  options.add_options()("clkout3", po::value<float>(), "Secondary Output(3) frequency in MHz");
  options.add_options()("phase3", po::value<float>()->default_value(0), "Secondary Output(3) phase in degrees");
  options.add_options()("file,f", po::value<string>(), "Output to file");
  options.add_options()("highres", "Use secondary PLL output for higher frequency resolution");
  options.add_options()("dynamic", "Use dynamic clock control");
  options.add_options()("reset", "Enable reset input");
  options.add_options()("standby", "Enable standby input");
  options.add_options()("feedback_clkout", po::value<string>(), "Use Nth Output as feedback signal");
  options.add_options()("internal_feedback", "Use internal feedback (instead of external)");
  options.add_options()("internal_feedback_wake", "Wake internal feedback");

  po::variables_map vm;
  po::parsed_options parsed = po::command_line_parser(argc, argv).options(options).run();
  po::store(parsed, vm);
  po::notify(vm);

  if(vm.count("help")){
    cerr << "Project Trellis - Open Source Tools for ECP5 FPGAs" << endl;
    cerr << argv[0] << ": ECP5 PLL Configuration Calculator" << endl;
    cerr << "Version " << git_describe_str << endl;
    cerr << endl;
    cerr << "This tool is experimental! Use at your own risk!" << endl;
    cerr << endl;
    cerr << "Copyright (C) 2018-2019 David Shah <david@symbioticeda.com>" << endl;
    cerr << endl;
    cerr << options << endl;
    return 1;
  }
  if(vm.count("clkin") != 1 || vm.count("clkout0") != 1){
    cerr << "Error: missing input or output frequency!\n";
    return 1;
  }
  float inputf = vm["clkin"].as<float>();
  float outputf = vm["clkout0"].as<float>();
  if(inputf < INPUT_MIN || inputf > INPUT_MAX){
    cerr << "Warning: Input frequency " << inputf << "MHz not in range (" << INPUT_MIN << "MHz, " << INPUT_MAX << "MHz)\n";
  }
  if(outputf < OUTPUT_MIN || outputf > OUTPUT_MAX){
    cerr << "Warning: Output frequency " << outputf << "MHz not in range (" << OUTPUT_MIN << "MHz, " << OUTPUT_MAX << "MHz)\n";
  }

  pll_params params = {};

  string module_name = "pll";
  if(vm.count("module"))
    module_name = vm["module"].as<string>();
  params.clkin_frequency = inputf;

  params.clkin_name = "clkin";
  if(vm.count("clkin_name"))
    params.clkin_name = vm["clkin_name"].as<string>();

  params.clkout0_name = "clkout0";
  if(vm.count("clkout0_name"))
    params.clkout0_name = vm["clkout0_name"].as<string>();

  params.secondary[0].name = "clkout[1]";
  params.secondary[1].name = "clkout[2]";
  params.secondary[2].name = "clkout[3]";

  if(vm.count("highres"))
  {
    if(vm.count("clkout1") > 0)
    {
      cerr << "Cannot specify secondary frequency in highres mode\n";
    }
    params.secondary[0].name = "clkout1";
    if(vm.count("clkout1_name"))
      params.secondary[0].name = vm["clkout1_name"].as<string>();
    calc_pll_params_highres(params, inputf, outputf);
  }
  else
  {
    calc_pll_params(params, inputf, outputf);
    if(vm.count("clkout1"))
    {
      string clkout1_name = "clkout1";
      if(vm.count("clkout1_name"))
        clkout1_name = vm["clkout1_name"].as<string>();
      generate_secondary_output(params, 0, clkout1_name, vm["clkout1"].as<float>(), vm["phase1"].as<float>());
    }
    if(vm.count("clkout2"))
    {
      string clkout2_name = "clkout2";
      if(vm.count("clkout2_name"))
        clkout2_name = vm["clkout2_name"].as<string>();
      generate_secondary_output(params, 1, clkout2_name, vm["clkout2"].as<float>(), vm["phase2"].as<float>());
    }
    if(vm.count("clkout3"))
    {
      string clkout3_name = "clkout3";
      if(vm.count("clkout3_name"))
        clkout3_name = vm["clkout3_name"].as<string>();
      generate_secondary_output(params, 2, clkout3_name, vm["clkout3"].as<float>(), vm["phase3"].as<float>());
    }
  }

  params.dynamic = 0;
  if(vm.count("dynamic"))
    params.dynamic = 1;
  params.reset = 0;
  if(vm.count("reset"))
    params.reset = 1;
  params.standby = 0;
  if(vm.count("standby"))
    params.standby = 1;
  params.feedback_name[0] = "OP";
  params.feedback_name[1] = "OS";
  params.feedback_name[2] = "OS2";
  params.feedback_name[3] = "OS3";
  params.feedback_wname[0] = params.clkout0_name;
  params.feedback_wname[1] = params.secondary[0].name;
  params.feedback_wname[2] = params.secondary[1].name;
  params.feedback_wname[3] = params.secondary[2].name;
  params.feedback_clkout = 0;
  if(vm.count("feedback_clkout"))
  {
    if(vm["feedback_clkout"].as<string>() == "0")
      params.feedback_clkout = 0;
    if(vm["feedback_clkout"].as<string>() == "1")
      params.feedback_clkout = 1;
    if(vm["feedback_clkout"].as<string>() == "2")
      params.feedback_clkout = 2;
    if(vm["feedback_clkout"].as<string>() == "3")
      params.feedback_clkout = 3;
  }
  params.internal_feedback = 0;
  if(vm.count("internal_feedback"))
    params.internal_feedback = 1;
  params.internal_feedback_wake = 0;
  if(vm.count("internal_feedback_wake"))
    params.internal_feedback_wake = 1;

  cout << "Pll parameters:" << endl;
  cout << "Refclk divisor: " << params.refclk_div << endl;
  cout << "Feedback divisor: " << params.feedback_div << endl;
  cout << "clkout0 divisor: " << params.output_div << "" << endl;
  cout << "clkout0 frequency: " << params.fout << " MHz" << endl;
  if(params.secondary[0].enabled){
    cout << "clkout1 divisor: " << params.secondary[0].div << endl;
    cout << "clkout1 frequency: " << params.secondary[0].freq << " MHz" << endl;
    cout << "clkout1 phase shift: " << params.secondary[0].phase << " degrees" << endl;
  }
  if(params.secondary[1].enabled){
    cout << "clkout2 divisor: " << params.secondary[1].div << endl;
    cout << "clkout2 frequency: " << params.secondary[1].freq << " MHz" << endl;
    cout << "clkout2 phase shift: " << params.secondary[1].phase << " degrees" << endl;
  }
  if(params.secondary[2].enabled){
    cout << "clkout3 divisor: " << params.secondary[2].div << endl;
    cout << "clkout3 frequency: " << params.secondary[2].freq << " MHz" << endl;
    cout << "clkout3 phase shift: " << params.secondary[2].phase << " degrees" << endl;
  }
  cout << "VCO frequency: " << params.fvco << endl;
  if(vm.count("file")){
    ofstream f;
    f.open(vm["file"].as<string>().c_str());
    write_pll_config(params, module_name, f);
    f.close();
  }
}

void calc_pll_params(pll_params &params, float input, float output){
  float error = std::numeric_limits<float>::max();
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
}

void calc_pll_params_highres(pll_params &params, float input, float output){
  float error = std::numeric_limits<float>::max();
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
}


void generate_secondary_output(pll_params &params, int channel, string name, float frequency, float phase){
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
  params.secondary[channel].name = name;
}

void write_pll_config(const pll_params & params, const string &name, ofstream& file)
{
  file << "// diamond 3.7 accepts this PLL\n";
  file << "// diamond 3.8-3.9 is untested\n";
  file << "// diamond 3.10 or higher is likely to abort with error about unable to use feedback signal\n";
  file << "// cause of this could be from wrong CPHASE/FPHASE parameters\n";
  file << "module " << name << "\n(\n";
  if(params.reset)
    file << "    input reset, // 0:inactive, 1:reset\n";
  if(params.standby)
    file << "    input standby, // 0:inactive, 1:standby\n";
  if(params.dynamic)
  {
    file << "    input [1:0] phasesel, // clkout[] index affected by dynamic phase shift (except clkfb), 5 ns min before apply\n";
    file << "    input phasedir, // 0:delayed (lagging), 1:advence (leading), 5 ns min before apply\n";
    file << "    input phasestep, // 45 deg step, high for 5 ns min, falling edge = apply\n";
    file << "    input phaseloadreg, // high for 10 ns min, falling edge = apply\n";
  }
  file << "    input " << params.clkin_name << ", // " << params.clkin_frequency << " MHz, 0 deg\n";
  file << "    output " << params.clkout0_name << ", // " << params.fout << " MHz, 0 deg\n";

  for(int i=0;i<3;i++){
    if(!(i==0 && params.mode == pll_mode::HIGHRES) && params.secondary[i].enabled){
      file << "    output " << params.secondary[i].name << ", // " << params.secondary[i].freq << " MHz, " << params.secondary[i].phase << " deg\n";
    }
  }

  file << "    output locked\n";
  file << ");\n";
  if(params.internal_feedback)
    file << "wire clkfb;\n";
  if(params.dynamic)
  {
    file << "wire [1:0] phasesel_hw;\n";
    file << "assign phasesel_hw = phasesel - 1;\n";
  }
  file << "(* FREQUENCY_PIN_CLKI=\"" << params.clkin_frequency << "\" *)\n";
  file << "(* FREQUENCY_PIN_CLKOP=\"" << params.fout << "\" *)\n";
  if(params.secondary[0].enabled)
    file << "(* FREQUENCY_PIN_CLKOS=\"" << params.secondary[0].freq << "\" *)\n";
  if(params.secondary[1].enabled)
    file << "(* FREQUENCY_PIN_CLKOS2=\"" << params.secondary[1].freq << "\" *)\n";
  if(params.secondary[2].enabled)
    file << "(* FREQUENCY_PIN_CLKOS3=\"" << params.secondary[2].freq << "\" *)\n";
  file << "(* ICP_CURRENT=\"12\" *) (* LPF_RESISTOR=\"8\" *) (* MFG_ENABLE_FILTEROPAMP=\"1\" *) (* MFG_GMCREF_SEL=\"2\" *)\n";
  file << "EHXPLLL #(\n";
  file << "        .PLLRST_ENA(\"" << (params.reset ? "EN" :"DIS") << "ABLED\"),\n";
  file << "        .INTFB_WAKE(\"" << (params.internal_feedback_wake ? "EN" :"DIS") << "ABLED\"),\n";
  file << "        .STDBY_ENABLE(\"" << (params.standby ? "EN" :"DIS") << "ABLED\"),\n";
  file << "        .DPHASE_SOURCE(\"" << (params.dynamic ? "EN" :"DIS") << "ABLED\"),\n";
  file << "        .OUTDIVIDER_MUXA(\"DIVA\"),\n";
  file << "        .OUTDIVIDER_MUXB(\"DIVB\"),\n";
  file << "        .OUTDIVIDER_MUXC(\"DIVC\"),\n";
  file << "        .OUTDIVIDER_MUXD(\"DIVD\"),\n";
  file << "        .CLKI_DIV(" << params.refclk_div <<"),\n";
  file << "        .CLKOP_ENABLE(\"ENABLED\"),\n";
  file << "        .CLKOP_DIV(" << params.output_div << "),\n";
  file << "        .CLKOP_CPHASE(" << params.primary_cphase << "),\n";
  file << "        .CLKOP_FPHASE(0),\n";
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
  if(params.internal_feedback)
    file << "        .FEEDBK_PATH(\"INT_" <<  params.feedback_name[params.feedback_clkout] << "\"),\n";
  else
    file << "        .FEEDBK_PATH(\"CLK" <<  params.feedback_name[params.feedback_clkout] << "\"),\n";
  file << "        .CLKFB_DIV(" << params.feedback_div << ")\n";
  file << "    ) pll_i (\n";
  if(params.reset)
    file << "        .RST(reset),\n";
  else
    file << "        .RST(1'b0),\n";
  if(params.standby)
    file << "        .STDBY(standby),\n";
  else
    file << "        .STDBY(1'b0),\n";
  file << "        .CLKI(" << params.clkin_name << "),\n";
  file << "        .CLKOP(" << params.clkout0_name << "),\n";
  if(params.secondary[0].enabled){
    if(params.mode == pll_mode::HIGHRES)
      file << "        .CLKOS(" << params.clkout0_name << "),\n";
    else
      file << "        .CLKOS(" << params.secondary[0].name << "),\n";
  }
  if(params.secondary[1].enabled){
    file << "        .CLKOS2(" << params.secondary[1].name << "),\n";
  }
  if(params.secondary[2].enabled){
    file << "        .CLKOS3(" << params.secondary[2].name << "),\n";
  }
  if(params.internal_feedback)
  {
    file << "        .CLKFB(clkfb),\n";
    file << "        .CLKINTFB(clkfb),\n";
  }
  else
  {
    file << "        .CLKFB(" <<  params.feedback_wname[params.feedback_clkout] << "),\n";
    file << "        .CLKINTFB(),\n";
  }
  if(params.dynamic)
  {
    file << "        .PHASESEL0(phasesel_hw[0]),\n";
    file << "        .PHASESEL1(phasesel_hw[1]),\n";
    file << "        .PHASEDIR(phasedir),\n";
    file << "        .PHASESTEP(phasestep),\n";
    file << "        .PHASELOADREG(phaseloadreg),\n";
  }
  else
  {
    file << "        .PHASESEL0(1'b0),\n";
    file << "        .PHASESEL1(1'b0),\n";
    file << "        .PHASEDIR(1'b1),\n";
    file << "        .PHASESTEP(1'b1),\n";
    file << "        .PHASELOADREG(1'b1),\n";
  }
  file << "        .PLLWAKESYNC(1'b0),\n";
  file << "        .ENCLKOP(1'b0),\n";
  file << "        .LOCK(locked)\n";
  file << "	);\n";
  file << "endmodule\n";
}
