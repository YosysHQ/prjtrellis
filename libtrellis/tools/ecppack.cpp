#include "ChipConfig.hpp"
#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "DatabasePath.hpp"
#include "Tile.hpp"
#include "BitDatabase.hpp"
#include "version.hpp"

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

uint32_t convert_hexstring(std::string value_str)
{
    return uint32_t(strtoul(value_str.c_str(), nullptr, 0));
}

enum class xsvf_instr : uint8_t {
    XCOMPLETE = 0x00,
    XTDOMASK = 0x01,
    XSIR = 0x02,
    XSDR = 0x03,
    XRUNTEST = 0x04,
    XREPEAT = 0x07,
    XSDRSIZE = 0x08,
    XSDRTDO = 0x09,
    XSTATE = 0x12,
    XENDIR = 0x13,
    XENDDR = 0x14,
    XWAITSTATE = 0x18,
    LCOUNT = 0x19,
    LDELAY = 0x1A,
    LSDR = 0x1B
};

enum class jtag_state : uint8_t {
    RESET = 0x00,
    IDLE = 0x01,
    DRPAUSE = 0x06,
    IRPAUSE = 0x0D
};

class VectorWriter {
public:
    virtual void header() = 0;
    virtual void state( jtag_state s ) = 0;
    virtual void sir( uint8_t instr, std::string comment ) = 0;
    // start an SDR command (output instruction and length; other arguments
    // will follow with sdr_continue()
    virtual void sdr( int len ) = 0;
    // append TDI bits to an SDR command started with sdr()
    virtual void sdr_continue( uint8_t tdi ) = 0;
    // finish the SDR command started with sdr() and sdr_continue()
    virtual void sdr_complete() = 0;
    virtual void sdr( int len, uint32_t tdi ) = 0;
    virtual void sdr( int len, uint32_t tdi, uint32_t tdo, uint32_t mask ) = 0;
    virtual void runtest( int ticks, int usecs ) = 0;
    virtual void poll( int len, uint32_t tdi, uint32_t tdo, uint32_t mask, int ticks, int usecs ) {
	// try to poll the scanned out data until we get a match... if we
	// can't do that, just wait a while and try once
	runtest( ticks, usecs );
	sdr( len, tdi, tdo, mask );
    }
    virtual void space() {}
    virtual void complete() = 0;
    virtual ~VectorWriter() {}
};

class SVFWriter : public VectorWriter {
private:
    ostream &s;
    vector<uint8_t> sdr_buf;
    bool odd_hex;
    int line;
    
public:
    SVFWriter( ostream &s ) : s(s), sdr_buf() {}

    virtual void header() {
	s << "HDR\t0;" << endl;
	s << "HIR\t0;" << endl;
	s << "TDR\t0;" << endl;
	s << "TIR\t0;" << endl;
	// these are critical: the ECP5 aborts configuration updates if we
	// pass through an update->idle path during the scan
	s << "ENDDR\tDRPAUSE;" << endl;
	s << "ENDIR\tIRPAUSE;" << endl;
    }
    
    virtual void state( jtag_state st ) {
	if( st == jtag_state::IDLE )
	    s << "STATE\tIDLE;" << endl;
	else if( st == jtag_state::RESET )
	    s << "STATE\tRESET;" << endl;
	else
	    throw logic_error( "unknown state" );
    }
    
    virtual void sir( uint8_t instr, std::string comment ) {
	s << "SIR\t8\tTDI  (" << setw(2) << hex << uppercase << setfill('0') << int(instr) << ");    ! " << comment << endl;
    }
    
    virtual void sdr( int len ) {
	s << "SDR\t" << setw(0) << dec << len << "\tTDI  (";
	sdr_buf.reserve( (len + 7) >> 3 );
	odd_hex = len & 4;
	line = 0;
    }
    
    virtual void sdr_continue( uint8_t tdi ) {
	if (line>39) {
	    s << endl << "\t\t\t";
	    line = 0;
	}
	
	s << setw(odd_hex ? 1 : 2) << hex << uppercase << int(tdi);
	odd_hex = 0;
	line++;
    }
    
    virtual void sdr_complete() {
	s << ");" << endl;
    }
    
    virtual void sdr( int len, uint32_t tdi ) {
	s << "SDR\t" << setw(0) << dec << len <<
	    "\tTDI  (" << setw((len + 3) >> 2) << hex << tdi << ");" << endl;
    }
    
    virtual void sdr( int len, uint32_t tdi, uint32_t tdo, uint32_t mask ) {
	s << "SDR\t" << setw(0) << dec << len <<
	    "\tTDI  (" << setw((len + 3) >> 2) << hex << tdi << ")" << endl <<
	    "\tTDO  (" << setw((len + 3) >> 2) << hex << tdo << ")" << endl <<
	    "\tMASK  (" << setw((len + 3) >> 2) << hex << mask << ");" << endl;
    }

    virtual void runtest( int ticks, int usecs ) {
	s << "RUNTEST\tIDLE\t" << setw(0) << dec << ticks << " TCK\t" << usecs << "E-6 SEC;" << endl;
    }
    
    virtual void space() {
	s << endl;
    }

    virtual void complete() {}
};

class XSVFWriter : public VectorWriter {
private:
    ostream &s;
    uint32_t xsdrsize;
    uint32_t tdoexpect, tdomask; // used only for <=32 bits
    bool mask_valid;
    bool expected_valid;
    
    void write( uint32_t val, int len ) {
	if( len > 24 )
	    s << uint8_t( ( val >> 24 ) & 0xFF );
	if( len > 16 )
	    s << uint8_t( ( val >> 16 ) & 0xFF );
	if( len > 8 )
	    s << uint8_t( ( val >> 8 ) & 0xFF );
	s << uint8_t( val & 0xFF );
    }
    
    void setsize( uint32_t len, bool clear_mask ) {
	if (xsdrsize == len)
	    return;

	s << uint8_t( xsvf_instr::XSDRSIZE );
	write( len, 32 );

	if( clear_mask ) {
	    s << uint8_t( xsvf_instr::XTDOMASK );
	    for (int i = 0; i < int(len + 7) >> 3; i++ )
		s << uint8_t( 0x00 );
	}

	xsdrsize = len;
	mask_valid = clear_mask;
	expected_valid = false;
    }
    
public:
    XSVFWriter( ostream &s ) : s(s), xsdrsize(0xFFFFFFFF), mask_valid(false),
			       expected_valid(false) {}

    virtual void header() {
	// these are critical: ECP5s abort configuration updates if we
	// pass through an update->idle path during the scan
	s << uint8_t( xsvf_instr::XENDDR ) << uint8_t( 0x01 ) <<
	    uint8_t( xsvf_instr::XENDIR ) << uint8_t( 0x01 ) <<
	    uint8_t( xsvf_instr::XREPEAT ) << uint8_t( 0x00 ) <<
	    // this is for XSVFWriter::poll(...)
	    uint8_t( xsvf_instr::LCOUNT ) << uint8_t( 0x00 ) <<
	    uint8_t( 0x00 ) << uint8_t( 0x00 ) << uint8_t( 0x10 );
    }
    
    virtual void state( enum jtag_state st ) {
	s << uint8_t( xsvf_instr::XSTATE ) << uint8_t( st );
    }
    
    virtual void sir( uint8_t instr, std::string comment ) {
	(void) comment;
	s << uint8_t( xsvf_instr::XSIR ) << uint8_t( 0x08 ) << uint8_t( instr );
    }
    
    virtual void sdr( int len ) {
	setsize( len, true );
	s << uint8_t( expected_valid ? xsvf_instr::XSDR : xsvf_instr::XSDRTDO );
    }
    
    virtual void sdr_continue( uint8_t tdi ) {
	s << tdi;
    }
    
    virtual void sdr_complete() {
	if( !expected_valid ) {
	    for (int i = 0; i < int(xsdrsize + 7) >> 3; i++ )
		s << uint8_t( 0x00 );
	    expected_valid = true;
	}
    }
    
    virtual void sdr( int len, uint32_t tdi ) {
	sdr( len, tdi, 0x00000000, 0x00000000 );
    }
    
    virtual void sdr( int len, uint32_t tdi, uint32_t tdo, uint32_t mask ) {
	setsize( len, false );
	if( !mask_valid || tdomask != mask ) {
	    s << uint8_t( xsvf_instr::XTDOMASK );
	    write( mask, len );
	    mask_valid = true;
	    tdomask = mask;
	}
	if (tdoexpect != tdo)
	    expected_valid = false;
	s << uint8_t( expected_valid ? xsvf_instr::XSDR : xsvf_instr::XSDRTDO );
	write( tdi, len );
	if( !expected_valid ) {
	    write( tdo, len );
	    expected_valid = true;
	    tdoexpect = tdo;
	}
    }
    
    virtual void runtest( int ticks, int usecs ) {
	s << uint8_t( xsvf_instr::XWAITSTATE ) << uint8_t( jtag_state::IDLE ) <<
	    uint8_t( jtag_state::IDLE );
	write( ticks, 32 );
	write( usecs, 32 );
    }
    
    virtual void poll( int len, uint32_t tdi, uint32_t tdo, uint32_t mask, int ticks, int usecs ) {
	// use the LDELAY/LSDR XSVF extensions to loop until the condition
	// is true (time out after 16 attempts, each for 1/8 of the
	// nominal time)
	ticks = (ticks + 0x07) >> 3;
	usecs = (usecs + 0x07) >> 3;
	s << uint8_t( xsvf_instr::LDELAY ) << uint8_t( jtag_state::IDLE );
	write( ticks, 32 );
	write( usecs, 32 );
	setsize( len, false );
	if( !mask_valid || tdomask != mask ) {
	    s << uint8_t( xsvf_instr::XTDOMASK );
	    write( mask, len );
	    mask_valid = true;
	    tdomask = mask;
	}
	s << uint8_t( xsvf_instr::LSDR );
	write( tdi, len );
	write( tdo, len );
	expected_valid = true;
	tdoexpect = tdo;
    }
    
    virtual void space() {}

    virtual void complete() {
	s << uint8_t( xsvf_instr::XCOMPLETE );
    }
};

int main(int argc, char *argv[])
{
    using namespace Trellis;
    namespace po = boost::program_options;

    std::string database_folder = get_database_path();

    po::options_description options("Allowed options");
    options.add_options()("help,h", "show help");
    options.add_options()("verbose,v", "verbose output");
    options.add_options()("db", po::value<std::string>(), "Trellis database folder location");
    options.add_options()("usercode", po::value<uint32_t>(), "USERCODE to set in bitstream");
    options.add_options()("idcode", po::value<std::string>(), "IDCODE to override in bitstream");
    options.add_options()("freq", po::value<std::string>(), "config frequency in MHz");
    options.add_options()("svf", po::value<std::string>(), "output SVF file");
    options.add_options()("xsvf", po::value<std::string>(), "output XSVF file");
    options.add_options()("svf-rowsize", po::value<int>(), "(X)SVF row size in bits (default 8000)");
    options.add_options()("svf-spibase", po::value<std::string>(), "Base address for (X)SVF SPI writes");
    options.add_options()("svf-spiflash", "(X)SVF output will write to SPI flash");
    options.add_options()("compress", "compress bitstream to reduce size");
    options.add_options()("spimode", po::value<std::string>(), "SPI Mode to use (fast-read, dual-spi, qspi)");
    options.add_options()("background", "enable background reconfiguration in bitstream");
    options.add_options()("delta", po::value<std::string>(), "create a delta partial bitstream given a reference config");
    options.add_options()("bootaddr", po::value<std::string>(), "set next BOOTADDR in bitstream and enable multi-boot");
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
    catch (po::required_option &e) {
        cerr << "Error: input file is mandatory." << endl << endl;
        goto help;
    }
    catch (std::exception &e) {
        cerr << "Error: " << e.what() << endl << endl;
        goto help;
    }

    if (vm.count("help")) {
help:
        cerr << "Project Trellis - Open Source Tools for ECP5 FPGAs" << endl;
        cerr << "Version " << git_describe_str << endl;
        cerr << argv[0] << ": ECP5 bitstream packer" << endl;
        cerr << endl;
        cerr << "Copyright (C) 2018 David Shah <david@symbioticeda.com>" << endl;
        cerr << endl;
        cerr << "Usage: " << argv[0] << " input.config [output.bit] [options]" << endl;
        cerr << options << endl;
        return vm.count("help") ? 0 : 1;
    }

    ifstream config_file(vm["input"].as<string>());
    if (!config_file) {
        cerr << "Failed to open input file" << endl;
        return 1;
    }

    if (vm.count("svf") && vm.count("xsvf")) {
        cerr << "Cannot output both SVF and XSVF" << endl;
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

    if (vm.count("spimode"))
        bitopts["spimode"] = vm["spimode"].as<string>();

    if (vm.count("compress"))
        bitopts["compress"] = "yes";

    if (vm.count("background")) {
        auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, "EFB0_PICB0"});
        auto esb = tile_db->get_data_for_enum("SYSCONFIG.BACKGROUND_RECONFIG");
        auto tile = c.get_tiles_by_type("EFB0_PICB0");
        for (const auto &bit : esb.options["ON"].bits)
            tile[0]->cram.set_bit(bit.frame, bit.bit, bit.inv ? 0 : 1);
        bitopts["background"] = "yes";
    }

    if (vm.count("bootaddr")) {
        uint32_t bootaddr = convert_hexstring(vm["bootaddr"].as<string>());

        if (bootaddr & 0xffff) {
            cerr << "Error: Boot Address must be 64k aligned !" << endl;
            return 1;
        }

        bootaddr = (bootaddr & 0x00ff0000) >> 16;

        auto tile_db = get_tile_bitdata(TileLocator{c.info.family, c.info.name, "EFB1_PICB1"});
        WordSettingBits wsb = tile_db->get_data_for_setword("BOOTADDR");
        auto tile = c.get_tiles_by_type("EFB1_PICB1");

        if (tile.size() != 1) {
            cerr << "EFB1_PICB1 Frame is wrong size. Can't proceed" << endl;
            return 1;
        }

        for(uint32_t j=0; j < wsb.bits.size(); j++) {
            auto bg = wsb.bits.at(j);
            for (auto bit :  bg.bits) {
                bool value = (bootaddr & (1 << j)) > 0;
                tile[0]->cram.set_bit(bit.frame, bit.bit, value);
            }
        }

        bitopts["multiboot"] = "yes";
    }

    bool partial_mode = false;
    bool svfspiflash = vm.count("svf-spiflash");
    uint32_t spibase = 0;
    if (vm.count("svf-spibase")) {
        spibase = convert_hexstring(vm["svf-spibase"].as<string>());

        if (spibase & 0xffff) {
            cerr << "Error: Base Address must be 64k aligned !" << endl;
            return 1;
        }

        spibase = (spibase & 0x00ff0000) >> 16;
    }
    vector<uint32_t> partial_frames;
    if (vm.count("delta")) {
        ifstream delta_file(vm["delta"].as<string>());
        if (!delta_file) {
            cerr << "Failed to open reference config file" << endl;
            return 1;
        }
        string refcfg((std::istreambuf_iterator<char>(delta_file)), std::istreambuf_iterator<char>());

        ChipConfig ref_cc;
        try {
            ref_cc = ChipConfig::from_string(refcfg);
        } catch (runtime_error &e) {
            cerr << "Failed to process reference config: " << e.what() << endl;
            return 1;
        }
        Chip ref_c = ref_cc.to_chip();
        for (int frame = 0; frame < c.cram.frames(); frame++) {
            if (ref_c.cram.data->at(frame) != c.cram.data->at(frame)) {
                partial_frames.push_back(frame);
            }
        }

        partial_mode = true;
    }

    Bitstream b = partial_mode ? Bitstream::serialise_chip_partial(c, partial_frames, bitopts) : Bitstream::serialise_chip(c, bitopts);
    if (vm.count("bit")) {
        ofstream bit_file(vm["bit"].as<string>(), ios::binary);
        if (!bit_file) {
            cerr << "Failed to open output file" << endl;
            return 1;
        }
        b.write_bit(bit_file);
    }

    if (vm.count("svf") || vm.count("xsvf")) {
	bool xsvf = vm.count("xsvf");

        // Create JTAG bitstream without SPI flash related settings, as these
        // seem to confuse the chip sometimes when configuring over JTAG
        if (!bitopts.empty() && !vm.count("svf-spiflash") && !(bitopts.size() == 1 && bitopts.count("compress"))) {
            bitopts.clear();
            if (vm.count("background"))
                bitopts["background"] = "yes";
            if (vm.count("bootaddr"))
                bitopts["multiboot"] = "yes";
            if (vm.count("compress"))
                bitopts["compress"] = "yes";
            b = Bitstream::serialise_chip(c, bitopts);
        }

        vector<uint8_t> bitstream = b.get_bytes();
        int max_row_size = svfspiflash ? 2048 : 8000;
        if (vm.count("svf-rowsize"))
            max_row_size = vm["svf-rowsize"].as<int>();
        if ((max_row_size % 8) != 0 || max_row_size <= 0) {
            cerr << (xsvf ? "X" : "") << "SVF row size must be an exact positive number of bytes" << endl;
            return 1;
        }
        ofstream svf_file(vm[xsvf ? "xsvf" : "svf"].as<string>());
        if (!svf_file) {
            cerr << "Failed to open output " << (xsvf ? "X" : "") << "SVF file" << endl;
            return 1;
        }
	VectorWriter &v( *( xsvf ? static_cast<VectorWriter *>(new XSVFWriter( svf_file )) : new SVFWriter( svf_file ) ) );
	v.header();
	v.state( jtag_state::IDLE );
	v.sir( 0xE0, "READ_ID" );
	v.sdr( 32, 0x00000000, c.info.idcode, 0xFFFFFFFF );
	v.space();
        if (!partial_mode) {
	    v.sir( 0x1C, "LSC_PRELOAD" );
	    v.sdr( 510 );
	    v.sdr_continue( 0x3F );
	    for (int i = 0; i < 63; i++ )
		v.sdr_continue( 0xFF );
	    v.sdr_complete();
            v.space();
	    v.sir( 0xC6, "ISC_ENABLE" );
	    v.sdr( 8, 0x00 );
	    v.runtest( 2, 10000 );
            v.space();
	    v.sir( 0x0E, "ISC_ERASE" );
	    v.sdr( 8, 0x01 );
            v.space();
	    v.sir( 0x3C, "LSC_READ_STATUS" );
	    v.poll( 32, 0x00000000, 0x00000000, 0x0000B000, 2, 10000 ); // not encrypted, not busy, not failed
	    v.space();
        } else {
	    v.sir( 0x79, "LSC_REFRESH" );
	    v.runtest( 2, 10000 );
	    v.sir( 0x74, "ISC_ENABLE_X" );
	    v.sdr( 8, 0x00 );
	    v.runtest( 2, 10000 );
        }
	if (svfspiflash) {
	    v.state( jtag_state::RESET );
	    v.state( jtag_state::IDLE );
	    v.sir( 0xFF, "ISC_NOOP" );
	    v.runtest( 2, 10000 );
	    v.sir( 0x3A, "LSC_PROG_SPI" );
	    v.sdr( 16, 0x68FE );
	    v.runtest( 32, 10000 );
	    int erase_end = spibase + ( ( bitstream.size() + 0xFFFF ) >> 16 );
	    for(int i = spibase; i < erase_end; i++ ) {
		v.sdr( 8, 0x60 ); // 06, Write Enable
		v.sdr( 32, ( reverse_byte(uint8_t(i)) << 8 ) | 0x1B ); // D8, Block Erase
		v.poll( 16, 0x00A0, 0x00FF, 0xC100, 128, 800000 ); // 05, Read Status Register 1: not protect, not write enable, not busy
	    }
	} else {
	    v.sir( 0x46, "LSC_INIT_ADDRESS" );
	    v.sdr( 8, 0x01 );
	    v.runtest( 2, 10000 );
	    v.space();
	    v.sir( 0x7A, "LSC_BITSTREAM_BURST" );
	    v.runtest( 2, 10000 );
	}
        size_t i = 0;
        while(i < bitstream.size()) {
           size_t len = min(size_t(max_row_size / 8), bitstream.size() - i);
           if (len == 0)
               break;
	   if (svfspiflash)
	       v.sdr( 8, 0x60 ); // 06, Write Enable
	   v.sdr( 8 * len + (svfspiflash ? 32 : 0) );
	   for (int j = len - 1; j >= 0; j-- )
	       v.sdr_continue( reverse_byte(uint8_t(bitstream[j + i])) );
	   if (svfspiflash) {
	       v.sdr_continue( reverse_byte(uint8_t(i & 0xFF)) );
	       v.sdr_continue( reverse_byte(uint8_t((i >> 8) & 0xFF)) );
	       v.sdr_continue( reverse_byte(uint8_t(((i >> 16) + spibase) & 0xFF)) );
	       v.sdr_continue( 0x40 ); // 02, Page Program
	   }
	   v.sdr_complete();
	   if (svfspiflash)
	       v.poll( 16, 0x00A0, 0x00FF, 0xC100, 32, 5000 ); // 05, Read Status Register 1: not protect, not write enable, not busy
           i += len;
        }
        if (!partial_mode) {
	    v.space();
	    v.sir( 0xFF, "ISC_NOOP" );
	    v.runtest( 100, 10000 );
            v.space();
	    v.sir( 0xC0, "USERCODE" );
	    v.runtest( 2, 1000 );
	    v.sdr( 32, 0x00000000, 0x00000000, 0xFFFFFFFF );
        }
	v.sir( 0x26, "ISC_DISABLE" );
	v.runtest( 2, 200000 );
	v.space();
	v.sir( 0xFF, "ISC_NOOP" );
	v.space();
	if (svfspiflash) {
	    v.sir( 0x79, "LSC_REFRESH" );
	    v.sdr( 24, 0x000000, 0x000000, 0x000000 );
	} else if (!partial_mode) {
	    v.sir( 0x3C, "LSC_READ_STATUS" );
	    v.poll( 32, 0x00000000, 0x00000100, 0x00002100, 2, 1000 ); // done, not failed
        }
	v.complete();
	delete &v;
    }

    return 0;
}
