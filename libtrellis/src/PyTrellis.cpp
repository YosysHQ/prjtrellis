#include "Bitstream.hpp"
#include "Chip.hpp"
#include "ChipConfig.hpp"
#include "Database.hpp"
#include "Tile.hpp"
#include "BitDatabase.hpp"
#include "TileConfig.hpp"
#include "RoutingGraph.hpp"
#include "DedupChipdb.hpp"

#include <vector>
#include <string>
#include <iostream>

#ifdef INCLUDE_PYTHON

#include <boost/python.hpp>

#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>
#include <boost/python/exception_translator.hpp>
#include "set_indexing_suite.h"

using namespace boost::python;
using namespace Trellis;

void translate_bspe(const BitstreamParseError &e)
{
    // Use the Python 'C' API to set up an exception object
    PyErr_SetString(PyExc_ValueError, e.what());
}

void translate_dbce(const DatabaseConflictError &e)
{
    // Use the Python 'C' API to set up an exception object
    PyErr_SetString(PyExc_ValueError, e.what());
}


BOOST_PYTHON_MODULE (pytrellis)
{
    // Common Types
    class_<vector<string>>("StringVector")
            .def(vector_indexing_suite<vector<string>>());

    class_<vector<uint8_t>>("ByteVector")
            .def(vector_indexing_suite<vector<uint8_t>>());

    class_<vector<bool>>("BoolVector")
            .def(vector_indexing_suite<vector<bool>>());

    class_<std::pair<int, int> >("IntPair")
            .def_readwrite("first", &std::pair<int, int>::first)
            .def_readwrite("second", &std::pair<int, int>::second);

    // From Bitstream.cpp
    register_exception_translator<BitstreamParseError>(&translate_bspe);
    class_<Bitstream>("Bitstream", no_init)
            .def("read_bit", &Bitstream::read_bit_py)
            .staticmethod("read_bit")
            .def("serialise_chip", &Bitstream::serialise_chip)
            .staticmethod("serialise_chip")
            .def("write_bit", &Bitstream::write_bit_py)
            .def_readwrite("metadata", &Bitstream::metadata)
            .def_readwrite("data", &Bitstream::data)
        .def("deserialise_chip", static_cast<Chip (Bitstream::*)()>(&Bitstream::deserialise_chip));

    class_<DeviceLocator>("DeviceLocator")
            .def_readwrite("family", &DeviceLocator::family)
            .def_readwrite("device", &DeviceLocator::device);

    class_<TileLocator>("TileLocator", init<string, string, string>())
            .def_readwrite("family", &TileLocator::family)
            .def_readwrite("device", &TileLocator::device)
            .def_readwrite("tiletype", &TileLocator::tiletype);

    // From Chip.cpp
    class_<ChipInfo>("ChipInfo")
            .def_readwrite("name", &ChipInfo::name)
            .def_readwrite("family", &ChipInfo::family)
            .def_readwrite("idcode", &ChipInfo::idcode)
            .def_readonly("num_frames", &ChipInfo::num_frames)
            .def_readonly("bits_per_frame", &ChipInfo::bits_per_frame)
            .def_readonly("pad_bits_before_frame", &ChipInfo::pad_bits_before_frame)
            .def_readonly("pad_bits_after_frame", &ChipInfo::pad_bits_after_frame)
            .def_readonly("max_row", &ChipInfo::max_row)
            .def_readonly("max_col", &ChipInfo::max_col)
            .def_readonly("col_bias", &ChipInfo::col_bias);

    class_<map<string, shared_ptr<Tile>>>("TileMap")
            .def(map_indexing_suite<map<string, shared_ptr<Tile>>, true>());

    class_<vector<shared_ptr<Tile>>>("TileVector")
            .def(vector_indexing_suite<vector<shared_ptr<Tile>>, true>());

    class_<GlobalRegion>("GlobalRegion")
            .def_readwrite("name", &GlobalRegion::name)
            .def_readwrite("x0", &GlobalRegion::x0)
            .def_readwrite("y0", &GlobalRegion::y0)
            .def_readwrite("x1", &GlobalRegion::x1)
            .def_readwrite("y1", &GlobalRegion::y1)
            .def("matches", &GlobalRegion::matches);

    class_<vector<GlobalRegion>>("GlobalRegionVector")
            .def(vector_indexing_suite<vector<GlobalRegion>>());

    class_<TapSegment>("TapSegment")
            .def_readwrite("tap_col", &TapSegment::tap_col)
            .def_readwrite("lx0", &TapSegment::lx0)
            .def_readwrite("lx1", &TapSegment::lx1)
            .def_readwrite("rx0", &TapSegment::rx0)
            .def_readwrite("rx1", &TapSegment::rx1)
            .def("matches_left", &TapSegment::matches_left)
            .def("matches_right", &TapSegment::matches_right);

    enum_<TapDriver::TapDir>("TapDir")
            .value("LEFT", TapDriver::LEFT)
            .value("RIGHT", TapDriver::RIGHT);

    class_<TapDriver>("TapDriver")
            .def_readwrite("col", &TapDriver::col)
            .def_readwrite("dir", &TapDriver::dir);

    class_<vector<TapSegment>>("TapSegmentVector")
            .def(vector_indexing_suite<vector<TapSegment>>());

    class_<GlobalsInfo>("GlobalsInfo")
            .def_readwrite("quadrants", &GlobalsInfo::quadrants)
            .def_readwrite("tapsegs", &GlobalsInfo::tapsegs)
            .def("get_quadrant", &GlobalsInfo::get_quadrant)
            .def("get_tap_driver", &GlobalsInfo::get_tap_driver)
            .def("get_spine_driver", &GlobalsInfo::get_spine_driver);

    class_<Chip>("Chip", init<string>())
            .def(init<uint32_t>())
            .def(init<const ChipInfo &>())
            .def("get_tile_by_name", &Chip::get_tile_by_name)
            .def("get_tiles_by_position", &Chip::get_tiles_by_position)
            .def("get_tiles_by_type", &Chip::get_tiles_by_type)
            .def("get_all_tiles", &Chip::get_all_tiles)
            .def("get_max_row", &Chip::get_max_row)
            .def("get_max_col", &Chip::get_max_col)
            .def("get_routing_graph", &Chip::get_routing_graph)
            .def_readonly("info", &Chip::info)
            .def_readwrite("cram", &Chip::cram)
            .def_readwrite("tiles", &Chip::tiles)
            .def_readwrite("usercode", &Chip::usercode)
            .def_readwrite("metadata", &Chip::metadata)
            .def_readwrite("global_data", &Chip::global_data)
            .def(self - self);

    class_<ChipDelta>("ChipDelta")
            .def(map_indexing_suite<ChipDelta>());

    // From CRAM.cpp
    class_<ChangedBit>("ChangedBit")
            .def_readonly("frame", &ChangedBit::frame)
            .def_readonly("bit", &ChangedBit::bit)
            .def_readonly("delta", &ChangedBit::delta);

    class_<CRAMView>("CRAMView", no_init)
            .def("bit", &CRAMView::get_bit)
            .def("set_bit", &CRAMView::set_bit)
            .def("bits", &CRAMView::bits)
            .def("frames", &CRAMView::frames)
            .def("clear", &CRAMView::clear)
            .def(self - self);

    class_<CRAM>("CRAM", init<int, int>())
            .def("bit", &CRAM::get_bit)
            .def("set_bit", &CRAM::set_bit)
            .def("bits", &CRAM::bits)
            .def("frames", &CRAM::frames)
            .def("make_view", &CRAM::make_view);

    class_<CRAMDelta>("CRAMDelta")
            .def(vector_indexing_suite<CRAMDelta>());

    // From Tile.cpp
    def("get_row_col_pair_from_chipsize", get_row_col_pair_from_chipsize);

    class_<vector<SiteInfo>>("SiteInfoVector")
            .def(vector_indexing_suite<vector<SiteInfo>>());

    class_<SiteInfo>("SiteInfo")
            .def_readonly("type", &SiteInfo::type)
            .def_readonly("row", &SiteInfo::row)
            .def_readonly("col", &SiteInfo::col);

    class_<TileInfo>("TileInfo")
            .def_readonly("name", &TileInfo::name)
            .def_readonly("type", &TileInfo::type)
            .def_readonly("num_frames", &TileInfo::num_frames)
            .def_readonly("bits_per_frame", &TileInfo::bits_per_frame)
            .def_readonly("frame_offset", &TileInfo::frame_offset)
            .def_readonly("bit_offset", &TileInfo::bit_offset)
            .def_readonly("sites", &TileInfo::sites)
            .def("get_row_col", &TileInfo::get_row_col);

    class_<Tile, shared_ptr<Tile>>("Tile", no_init)
            .def_readonly("info", &Tile::info)
            .def_readwrite("cram", &Tile::cram)
            .def_readwrite("known_bits", &Tile::known_bits)
            .def_readwrite("unknown_bits", &Tile::unknown_bits)
            .def("dump_config", &Tile::dump_config)
            .def("read_config", &Tile::read_config);

    // From Database.cpp
    def("load_database", load_database);
    def("find_device_by_name", find_device_by_name);
    def("find_device_by_idcode", find_device_by_idcode);
    def("get_chip_info", get_chip_info);
    def("get_device_tilegrid", get_device_tilegrid);
    def("get_tile_bitdata", get_tile_bitdata);

    // From BitDatabase.cpp
    register_exception_translator<DatabaseConflictError>(&translate_dbce);
    class_<ConfigBit>("ConfigBit")
            .def_readwrite("frame", &ConfigBit::frame)
            .def_readwrite("bit", &ConfigBit::bit)
            .def_readwrite("inv", &ConfigBit::inv);

    def("cbit_from_str", cbit_from_str);
    class_<vector<ConfigBit>>("ConfigBitVector")
            .def(vector_indexing_suite<vector<ConfigBit>>());
    class_<set<ConfigBit>>("ConfigBitSet")
            .def(bond::python::set_indexing_suite<set<ConfigBit>, true>());

    class_<BitGroup>("BitGroup")
            .def(init<const CRAMDelta &>())
            .def_readwrite("bits", &BitGroup::bits)
            .def("match", &BitGroup::match)
            .def("add_coverage", &BitGroup::add_coverage)
            .def("set_group", &BitGroup::set_group)
            .def("clear_group", &BitGroup::clear_group);

    class_<vector<BitGroup>>("BitGroupVector")
            .def(vector_indexing_suite<vector<BitGroup>>());

    class_<ArcData>("ArcData")
            .def_readwrite("source", &ArcData::source)
            .def_readwrite("sink", &ArcData::sink)
            .def_readwrite("bits", &ArcData::bits);

    class_<map<string, ArcData>>("ArcDataMap")
            .def(map_indexing_suite<map<string, ArcData>>());

    class_<MuxBits>("MuxBits")
            .def_readwrite("sink", &MuxBits::sink)
            .def_readwrite("arcs", &MuxBits::arcs)
            .def("get_sources", &MuxBits::get_sources)
            .def("get_driver", &MuxBits::get_driver)
            .def("set_driver", &MuxBits::set_driver);

    class_<WordSettingBits>("WordSettingBits")
            .def_readwrite("name", &WordSettingBits::name)
            .def_readwrite("bits", &WordSettingBits::bits)
            .def_readwrite("defval", &WordSettingBits::defval)
            .def("get_value", &WordSettingBits::get_value)
            .def("set_value", &WordSettingBits::set_value);

    class_<map<string, BitGroup>>("BitGroupMap")
            .def(map_indexing_suite<map<string, BitGroup>>());

    class_<EnumSettingBits>("EnumSettingBits")
            .def_readwrite("name", &EnumSettingBits::name)
            .def_readwrite("options", &EnumSettingBits::options)
            .def("get_options", &EnumSettingBits::get_options)
            .add_property("defval", &EnumSettingBits::get_defval, &EnumSettingBits::set_defval)
            .def("get_value", &EnumSettingBits::get_value)
            .def("set_value", &EnumSettingBits::set_value);

    class_<FixedConnection>("FixedConnection")
            .def_readwrite("source", &FixedConnection::source)
            .def_readwrite("sink", &FixedConnection::sink);

    class_<vector<FixedConnection>>("FixedConnectionVector")
            .def(vector_indexing_suite<vector<FixedConnection>>());

    class_<TileBitDatabase, shared_ptr<TileBitDatabase>>("TileBitDatabase", no_init)
            .def("config_to_tile_cram", &TileBitDatabase::config_to_tile_cram)
            .def("tile_cram_to_config", &TileBitDatabase::tile_cram_to_config)
            .def("get_sinks", &TileBitDatabase::get_sinks)
            .def("get_mux_data_for_sink", &TileBitDatabase::get_mux_data_for_sink)
            .def("get_settings_words", &TileBitDatabase::get_settings_words)
            .def("get_data_for_setword", &TileBitDatabase::get_data_for_setword)
            .def("get_settings_enums", &TileBitDatabase::get_settings_enums)
            .def("get_data_for_enum", &TileBitDatabase::get_data_for_enum)
            .def("get_fixed_conns", &TileBitDatabase::get_fixed_conns)
            .def("get_downhill_wires", &TileBitDatabase::get_downhill_wires)
            .def("add_mux_arc", &TileBitDatabase::add_mux_arc)
            .def("add_setting_word", &TileBitDatabase::add_setting_word)
            .def("add_setting_enum", &TileBitDatabase::add_setting_enum)
            .def("add_fixed_conn", &TileBitDatabase::add_fixed_conn)
            .def("remove_fixed_sink", &TileBitDatabase::remove_fixed_sink)
            .def("remove_setting_word", &TileBitDatabase::remove_setting_word)
            .def("remove_setting_enum", &TileBitDatabase::remove_setting_enum)
            .def("save", &TileBitDatabase::save);

    typedef pair<string, bool> StringBoolPair;
    typedef pair<string, bool> StringBoolPair;
    class_<StringBoolPair>("StringBoolPair")
            .def_readwrite("first", &StringBoolPair::first)
            .def_readwrite("second", &StringBoolPair::second);

    class_<vector<StringBoolPair>>("StringBoolPairVector")
            .def(vector_indexing_suite<vector<StringBoolPair>>());

    // From TileConfig.hpp
    class_<ConfigArc>("ConfigArc")
            .def_readwrite("source", &ConfigArc::source)
            .def_readwrite("sink", &ConfigArc::sink);
    class_<ConfigWord>("ConfigWord")
            .def_readwrite("name", &ConfigWord::name)
            .def_readwrite("value", &ConfigWord::value);
    class_<ConfigEnum>("ConfigEnum")
            .def_readwrite("name", &ConfigEnum::name)
            .def_readwrite("value", &ConfigEnum::value);
    class_<ConfigUnknown>("ConfigUnknown")
            .def_readwrite("frame", &ConfigUnknown::frame)
            .def_readwrite("bit", &ConfigUnknown::bit);

    class_<vector<ConfigArc>>("ConfigArcVector")
            .def(vector_indexing_suite<vector<ConfigArc>>());
    class_<vector<ConfigWord>>("ConfigWordVector")
            .def(vector_indexing_suite<vector<ConfigWord>>());
    class_<vector<ConfigEnum>>("ConfigEnumVector")
            .def(vector_indexing_suite<vector<ConfigEnum>>());
    class_<vector<ConfigUnknown>>("ConfigUnknownVector")
            .def(vector_indexing_suite<vector<ConfigUnknown>>());

    class_<TileConfig>("TileConfig")
            .def_readwrite("carcs", &TileConfig::carcs)
            .def_readwrite("cwords", &TileConfig::cwords)
            .def_readwrite("cenums", &TileConfig::cenums)
            .def_readwrite("cunknowns", &TileConfig::cunknowns)
            .def("add_arc", &TileConfig::add_arc)
            .def("add_enum", &TileConfig::add_enum)
            .def("add_word", &TileConfig::add_word)
            .def("add_unknown", &TileConfig::add_unknown)
            .def("to_string", &TileConfig::to_string)
            .def("from_string", &TileConfig::from_string)
            .staticmethod("from_string");

    // From ChipConfig.hpp
    class_<map<string, TileConfig>>("TileConfigMap")
            .def(map_indexing_suite<map<string, TileConfig>>());
    class_<vector<uint16_t>>("Uint16Vector")
            .def(vector_indexing_suite<vector<uint16_t>>());
    class_<map<uint16_t, vector<uint16_t>>>("Uint16VMap")
            .def(map_indexing_suite<map<uint16_t, vector<uint16_t>>>());

    class_<ChipConfig>("ChipConfig")
            .def_readwrite("chip_name", &ChipConfig::chip_name)
            .def_readwrite("metadata", &ChipConfig::metadata)
            .def_readwrite("tiles", &ChipConfig::tiles)
            .def_readwrite("tilegroups", &ChipConfig::tilegroups)
            .def_readwrite("bram_data", &ChipConfig::bram_data)
            .def("to_string", &ChipConfig::to_string)
            .def("from_string", &ChipConfig::from_string)
            .staticmethod("from_string")
            .def("to_chip", &ChipConfig::to_chip)
            .def("from_chip", &ChipConfig::from_chip)
            .staticmethod("from_chip");

    // From RoutingGraph.hpp
    class_<Location>("Location", init<int, int>())
            .def_readwrite("x", &Location::x)
            .def_readwrite("y", &Location::y)
            .def(self + self)
            .def(self == self)
            .def(self != self);

    class_<RoutingId>("RoutingId")
            .def_readwrite("loc", &RoutingId::loc)
            .def_readwrite("id", &RoutingId::id)
            .def(self == self)
            .def(self != self);

    class_<vector<RoutingId>>("RoutingIdVector")
            .def(vector_indexing_suite<vector<RoutingId>>());

    typedef pair<RoutingId, ident_t> BelPin;
    class_<BelPin>("BelPin")
            .def_readwrite("bel", &BelPin::first)
            .def_readwrite("pin", &BelPin::second);

    typedef pair<RoutingId, PortDirection> BelWireDir;
    class_<BelWireDir>("BelWireDir")
            .def_readwrite("wire", &BelWireDir::first)
            .def_readwrite("dir", &BelWireDir::second);

    enum_<PortDirection>("PortDirection")
            .value("PORT_IN", PORT_IN)
            .value("PORT_OUT", PORT_OUT)
            .value("PORT_INOUT", PORT_INOUT);

    class_<vector<BelPin>>("BelPinVector")
            .def(vector_indexing_suite<vector<BelPin>>());

    class_<RoutingWire>("RoutingWire")
            .def_readwrite("id", &RoutingWire::id)
            .def_readwrite("uphill", &RoutingWire::uphill)
            .def_readwrite("downhill", &RoutingWire::downhill)
            .def_readwrite("belsUphill", &RoutingWire::belsUphill)
            .def_readwrite("belsDownhill", &RoutingWire::belsDownhill);

    class_<RoutingArc>("RoutingArc")
            .def_readwrite("id", &RoutingArc::id)
            .def_readwrite("tiletype", &RoutingArc::tiletype)
            .def_readwrite("source", &RoutingArc::source)
            .def_readwrite("sink", &RoutingArc::sink)
            .def_readwrite("configurable", &RoutingArc::configurable);

    class_<map<ident_t, BelWireDir>>("RoutingPinMap")
            .def(map_indexing_suite<map<ident_t, BelWireDir>>());

    class_<RoutingBel>("RoutingBel")
            .def_readwrite("name", &RoutingBel::name)
            .def_readwrite("type", &RoutingBel::type)
            .def_readwrite("pins", &RoutingBel::pins)
            .def_readwrite("z", &RoutingBel::z);

    class_<map<ident_t, RoutingWire>>("RoutingWireMap")
            .def(map_indexing_suite<map<ident_t, RoutingWire>>());

    class_<map<ident_t, RoutingArc>>("RoutingArcMap")
            .def(map_indexing_suite<map<ident_t, RoutingArc>>());

    class_<map<ident_t, RoutingBel>>("RoutingBelMap")
            .def(map_indexing_suite<map<ident_t, RoutingBel>>());

    class_<RoutingTileLoc>("RoutingTileLoc")
            .def_readwrite("loc", &RoutingTileLoc::loc)
            .def_readwrite("wires", &RoutingTileLoc::wires)
            .def_readwrite("arcs", &RoutingTileLoc::arcs)
            .def_readwrite("bels", &RoutingTileLoc::bels);

    class_<map<Location, RoutingTileLoc>>("RoutingTileMap")
            .def(map_indexing_suite<map<Location, RoutingTileLoc>>());

    class_<RoutingGraph, shared_ptr<RoutingGraph>>("RoutingGraph", no_init)
            .def_readonly("chip_name", &RoutingGraph::chip_name)
            .def_readonly("max_row", &RoutingGraph::max_row)
            .def_readonly("max_col", &RoutingGraph::max_col)
            .def("ident", &RoutingGraph::ident)
            .def("to_str", &RoutingGraph::to_str)
            .def("id_at_loc", &RoutingGraph::id_at_loc)
            .def_readwrite("tiles", &RoutingGraph::tiles)
            .def("globalise_net", &RoutingGraph::globalise_net)
            .def("add_arc", &RoutingGraph::add_arc)
            .def("add_wire", &RoutingGraph::add_wire);

    // DedupChipdb
    using namespace DDChipDb;
    class_<RelId>("RelId")
            .def_readwrite("rel", &RelId::rel)
            .def_readwrite("id", &RelId::id)
            .def(self == self)
            .def(self != self);

    class_<BelPort>("BelPort")
            .def_readwrite("bel", &BelPort::bel)
            .def_readwrite("pin", &BelPort::pin);
    class_<BelWire>("BelWire")
            .def_readwrite("wire", &BelWire::wire)
            .def_readwrite("pin", &BelWire::pin)
            .def_readwrite("dir", &BelWire::dir);

    class_<vector<BelPort>>("BelPortVector")
            .def(vector_indexing_suite<vector<BelPort>>());
    class_<vector<BelWire>>("BelWireVector")
            .def(vector_indexing_suite<vector<BelWire>>());
    class_<vector<RelId>>("RelIdVector")
            .def(vector_indexing_suite<vector<RelId>>());
    class_<set<RelId>>("RelIdSet")
            .def(bond::python::set_indexing_suite<set<RelId>,true>());

    enum_<ArcClass>("ArcClass")
            .value("ARC_STANDARD", ARC_STANDARD)
            .value("ARC_FIXED", ARC_FIXED);
    class_<DdArcData>("DdArcData")
            .def_readwrite("srcWire", &DdArcData::srcWire)
            .def_readwrite("sinkWire", &DdArcData::sinkWire)
            .def_readwrite("cls", &DdArcData::cls)
            .def_readwrite("delay", &DdArcData::delay)
            .def_readwrite("tiletype", &DdArcData::tiletype);

    class_<WireData>("WireData")
            .def_readwrite("name", &WireData::name)
            .def_readwrite("arcsDownhill", &WireData::arcsDownhill)
            .def_readwrite("arcsUphill", &WireData::arcsUphill)
            .def_readwrite("belPins", &WireData::belPins);

    class_<BelData>("BelData")
            .def_readwrite("name", &BelData::name)
            .def_readwrite("type", &BelData::type)
            .def_readwrite("z", &BelData::z)
            .def_readwrite("wires", &BelData::wires);

    class_<vector<BelData>>("BelDataVector")
            .def(vector_indexing_suite<vector<BelData>>());
    class_<vector<WireData>>("WireDataVector")
            .def(vector_indexing_suite<vector<WireData>>());
    class_<vector<DdArcData>>("DdArcDataVector")
            .def(vector_indexing_suite<vector<DdArcData>>());

    class_<LocationData>("LocationData")
            .def_readwrite("wires", &LocationData::wires)
            .def_readwrite("arcs", &LocationData::arcs)
            .def_readwrite("bels", &LocationData::bels)
            .def("checksum", &LocationData::checksum);

    class_<map<Location, checksum_t>>("LocationMap")
            .def(map_indexing_suite<map<Location, checksum_t>>());

    class_<map<checksum_t, LocationData>>("LocationTypesMap")
            .def(map_indexing_suite<map<checksum_t, LocationData>>());

    class_<checksum_t>("checksum_t")
            .def_readwrite("first", &checksum_t::first)
            .def_readwrite("second", &checksum_t::second)
            .def(self == self);

    class_<DedupChipdb, shared_ptr<DedupChipdb>>("DedupChipdb")
            .def_readwrite("locationTypes", &DedupChipdb::locationTypes)
            .def_readwrite("typeAtLocation", &DedupChipdb::typeAtLocation)
            .def("get_cs_data", &DedupChipdb::get_cs_data)
            .def("ident", &DedupChipdb::ident)
            .def("to_str", &DedupChipdb::to_str);

    def("make_dedup_chipdb", make_dedup_chipdb);
}

#endif
