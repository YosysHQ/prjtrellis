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

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl_bind.h>

using namespace pybind11;
using namespace Trellis;
using namespace DDChipDb;

namespace py = pybind11;

typedef pair<int, int> IntPair;
typedef pair<string, bool> StringBoolPair;
typedef pair<RoutingId, ident_t> BelPin;
typedef pair<RoutingId, PortDirection> BelWireDir;

// Common Types
PYBIND11_MAKE_OPAQUE(IntPair)
PYBIND11_MAKE_OPAQUE(LocationData)
PYBIND11_MAKE_OPAQUE(checksum_t)
PYBIND11_MAKE_OPAQUE(map<checksum_t, LocationData>)
PYBIND11_MAKE_OPAQUE(Location)

PYBIND11_MODULE (pytrellis, m)
{
    // Common Types
    py::bind_vector<vector<string>>(m, "StringVector");

    py::bind_vector<vector<uint8_t>>(m, "ByteVector");

    py::bind_vector<vector<bool>>(m, "BoolVector");

    class_<IntPair>(m, "IntPair")
            .def_readonly("first", &std::pair<int, int>::first)
            .def_readonly("second", &std::pair<int, int>::second);

    m.def("make_IntPair", [](int first, int second) {
        return std::make_pair(first, second);
    });

    // From Bitstream.cpp
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p)
                std::rethrow_exception(p);
        } catch (const BitstreamParseError &e) {
            PyErr_SetString(PyExc_ValueError, e.what());
        } catch (const DatabaseConflictError &e) {
            PyErr_SetString(PyExc_ValueError, e.what());
        }
    });

    class_<Bitstream>(m, "Bitstream")
            .def_static("read_bit", &Bitstream::read_bit_py)
            .def_static("serialise_chip", &Bitstream::serialise_chip_py)
            .def_static("serialise_chip_delta", &Bitstream::serialise_chip_delta_py)
            .def("write_bit", &Bitstream::write_bit_py)
            .def_readwrite("metadata", &Bitstream::metadata)
            .def_readwrite("data", &Bitstream::data)
            .def("deserialise_chip", static_cast<Chip (Bitstream::*)()>(&Bitstream::deserialise_chip));

    class_<DeviceLocator>(m, "DeviceLocator")
            .def_readwrite("family", &DeviceLocator::family)
            .def_readwrite("device", &DeviceLocator::device)
            .def_readwrite("variant", &DeviceLocator::variant);

    class_<TileLocator>(m, "TileLocator")
            .def(init<string, string, string>())
            .def_readwrite("family", &TileLocator::family)
            .def_readwrite("device", &TileLocator::device)
            .def_readwrite("tiletype", &TileLocator::tiletype);

    // From Chip.cpp
    class_<ChipInfo>(m, "ChipInfo")
            .def_readwrite("name", &ChipInfo::name)
            .def_readwrite("family", &ChipInfo::family)
            .def_readwrite("variant", &ChipInfo::variant)
            .def_readwrite("idcode", &ChipInfo::idcode)
            .def_readonly("num_frames", &ChipInfo::num_frames)
            .def_readonly("bits_per_frame", &ChipInfo::bits_per_frame)
            .def_readonly("pad_bits_before_frame", &ChipInfo::pad_bits_before_frame)
            .def_readonly("pad_bits_after_frame", &ChipInfo::pad_bits_after_frame)
            .def_readonly("max_row", &ChipInfo::max_row)
            .def_readonly("max_col", &ChipInfo::max_col)
            .def_readonly("row_bias", &ChipInfo::row_bias)
            .def_readonly("col_bias", &ChipInfo::col_bias);

    py::bind_map<map<string, shared_ptr<Tile>>>(m, "TileMap");

    py::bind_vector<vector<shared_ptr<Tile>>>(m, "TileVector");

    class_<GlobalRegion>(m, "GlobalRegion")
            .def_readwrite("name", &GlobalRegion::name)
            .def_readwrite("x0", &GlobalRegion::x0)
            .def_readwrite("y0", &GlobalRegion::y0)
            .def_readwrite("x1", &GlobalRegion::x1)
            .def_readwrite("y1", &GlobalRegion::y1)
            .def("matches", &GlobalRegion::matches);

    py::bind_vector<vector<GlobalRegion>>(m, "GlobalRegionVector");

    class_<TapSegment>(m, "TapSegment")
            .def_readwrite("tap_col", &TapSegment::tap_col)
            .def_readwrite("lx0", &TapSegment::lx0)
            .def_readwrite("lx1", &TapSegment::lx1)
            .def_readwrite("rx0", &TapSegment::rx0)
            .def_readwrite("rx1", &TapSegment::rx1)
            .def("matches_left", &TapSegment::matches_left)
            .def("matches_right", &TapSegment::matches_right);

    enum_<TapDriver::TapDir>(m, "TapDir")
            .value("LEFT", TapDriver::LEFT)
            .value("RIGHT", TapDriver::RIGHT);

    class_<TapDriver>(m, "TapDriver")
            .def_readwrite("col", &TapDriver::col)
            .def_readwrite("dir", &TapDriver::dir);

    py::bind_vector<vector<TapSegment>>(m, "TapSegmentVector");

    class_<Ecp5GlobalsInfo>(m, "Ecp5GlobalsInfo")
            .def_readwrite("quadrants", &Ecp5GlobalsInfo::quadrants)
            .def_readwrite("tapsegs", &Ecp5GlobalsInfo::tapsegs)
            .def("get_quadrant", &Ecp5GlobalsInfo::get_quadrant)
            .def("get_tap_driver", &Ecp5GlobalsInfo::get_tap_driver)
            .def("get_spine_driver", &Ecp5GlobalsInfo::get_spine_driver);

    class_<LeftRightConn>(m, "LeftRightConn")
            .def_readwrite("name", &LeftRightConn::name)
            .def_readwrite("row", &LeftRightConn::row)
            .def_readwrite("row_span", &LeftRightConn::row_span);

    class_<MissingDccs>(m, "MissingDccs")
            .def_readwrite("row", &MissingDccs::row)
            .def_readwrite("missing", &MissingDccs::missing);

    py::bind_vector<vector<LeftRightConn>>(m, "LeftRightConnVector");

    py::bind_vector<vector<vector<int>>>(m, "UpDownConnVector");

    py::bind_vector<vector<vector<std::pair<int, int>>>>(m, "BranchSpanVector");

    py::bind_vector<vector<MissingDccs>>(m, "MissingDccsVector");

    py::bind_vector<vector<int>>(m, "IntVector");

    py::bind_vector<vector<std::pair<int, int>>>(m, "IntPairVector");

    class_<MachXO2GlobalsInfo>(m, "MachXO2GlobalsInfo")
            .def_readwrite("lr_conns", &MachXO2GlobalsInfo::lr_conns)
            .def_readwrite("ud_conns", &MachXO2GlobalsInfo::ud_conns)
            .def_readwrite("branch_spans", &MachXO2GlobalsInfo::branch_spans)
            .def_readwrite("missing_dccs", &MachXO2GlobalsInfo::missing_dccs);

    class_<Chip>(m, "Chip")
            .def(init<string>())
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
            // Alias for backwards compatibility.
            .def_readwrite("global_data", &Chip::global_data_ecp5)
            .def_readwrite("global_data_ecp5", &Chip::global_data_ecp5)
            .def_readwrite("global_data_machxo2", &Chip::global_data_machxo2)
            .def(self - self);

    py::bind_map<ChipDelta>(m, "ChipDelta");

    // From CRAM.cpp
    class_<ChangedBit>(m, "ChangedBit")
            .def_readonly("frame", &ChangedBit::frame)
            .def_readonly("bit", &ChangedBit::bit)
            .def_readonly("delta", &ChangedBit::delta);

    class_<CRAMView>(m, "CRAMView")
            .def("bit", &CRAMView::get_bit)
            .def("set_bit", &CRAMView::set_bit)
            .def("bits", &CRAMView::bits)
            .def("frames", &CRAMView::frames)
            .def("clear", &CRAMView::clear)
            .def(self - self);

    class_<CRAM>(m, "CRAM")
            .def(init<int, int>())
            .def("bit", &CRAM::get_bit)
            .def("set_bit", &CRAM::set_bit)
            .def("bits", &CRAM::bits)
            .def("frames", &CRAM::frames)
            .def("make_view", &CRAM::make_view);

    py::bind_vector<CRAMDelta>(m, "CRAMDelta");

    // From Tile.cpp
    m.def("get_row_col_pair_from_chipsize", get_row_col_pair_from_chipsize);

    py::bind_vector<vector<SiteInfo>>(m, "SiteInfoVector");

    class_<SiteInfo>(m, "SiteInfo")
            .def_readonly("type", &SiteInfo::type)
            .def_readonly("row", &SiteInfo::row)
            .def_readonly("col", &SiteInfo::col);

    class_<TileInfo>(m, "TileInfo")
            .def_readonly("name", &TileInfo::name)
            .def_readonly("type", &TileInfo::type)
            .def_readonly("num_frames", &TileInfo::num_frames)
            .def_readonly("bits_per_frame", &TileInfo::bits_per_frame)
            .def_readonly("frame_offset", &TileInfo::frame_offset)
            .def_readonly("bit_offset", &TileInfo::bit_offset)
            .def_readonly("sites", &TileInfo::sites)
            .def("get_row_col", &TileInfo::get_row_col);

    class_<Tile, shared_ptr<Tile>>(m, "Tile")
            .def_readonly("info", &Tile::info)
            .def_readwrite("cram", &Tile::cram)
            .def_readwrite("known_bits", &Tile::known_bits)
            .def_readwrite("unknown_bits", &Tile::unknown_bits)
            .def("dump_config", &Tile::dump_config)
            .def("read_config", &Tile::read_config);

    // From Database.cpp
    m.def("load_database", load_database);
    m.def("find_device_by_name", find_device_by_name);
    m.def("find_device_by_name_and_variant", find_device_by_name_and_variant);
    m.def("find_device_by_idcode", find_device_by_idcode);
    m.def("find_device_by_frames", find_device_by_frames);
    m.def("get_chip_info", get_chip_info);
    m.def("get_device_tilegrid", get_device_tilegrid);
    m.def("get_tile_bitdata", get_tile_bitdata);

    // From BitDatabase.cpp
    class_<ConfigBit>(m, "ConfigBit")
            .def(init<>())
            .def_readwrite("frame", &ConfigBit::frame)
            .def_readwrite("bit", &ConfigBit::bit)
            .def_readwrite("inv", &ConfigBit::inv);

    m.def("cbit_from_str", cbit_from_str);
    py::bind_vector<vector<ConfigBit>>(m, "ConfigBitVector");
    class_<std::set<ConfigBit>>(m, "ConfigBitSet")
        .def("__len__", [](const std::set<ConfigBit> &v) { return v.size(); })
        .def("__iter__", [](std::set<ConfigBit> &v) {
            return py::make_iterator(v.begin(), v.end());
        }, py::keep_alive<0, 1>()) /* Keep vector alive while iterator is used */
        .def("add", [](std::set<ConfigBit> &v, const ConfigBit& value) { v.insert(value); });

    class_<BitGroup>(m, "BitGroup")
            .def(init<>())
            .def(init<const CRAMDelta &>())
            .def_readwrite("bits", &BitGroup::bits)
            .def("match", &BitGroup::match)
            .def("add_coverage", &BitGroup::add_coverage)
            .def("set_group", &BitGroup::set_group)
            .def("clear_group", &BitGroup::clear_group);

    py::bind_vector<vector<BitGroup>>(m, "BitGroupVector");

    class_<ArcData>(m, "ArcData")
            .def(init<>())
            .def_readwrite("source", &ArcData::source)
            .def_readwrite("sink", &ArcData::sink)
            .def_readwrite("bits", &ArcData::bits);

    py::bind_map<map<string, ArcData>>(m, "ArcDataMap");

    class_<MuxBits>(m, "MuxBits")
            .def_readwrite("sink", &MuxBits::sink)
            .def_readwrite("arcs", &MuxBits::arcs)
            .def("get_sources", &MuxBits::get_sources)
            .def("get_driver", &MuxBits::get_driver)
            .def("set_driver", &MuxBits::set_driver);

    class_<WordSettingBits>(m, "WordSettingBits")
            .def(init<>())
            .def_readwrite("name", &WordSettingBits::name)
            .def_readwrite("bits", &WordSettingBits::bits)
            .def_readwrite("defval", &WordSettingBits::defval)
            .def("get_value", &WordSettingBits::get_value)
            .def("set_value", &WordSettingBits::set_value);

    py::bind_map<map<string, BitGroup>>(m, "BitGroupMap");

    class_<EnumSettingBits>(m, "EnumSettingBits")
            .def(init<>())
            .def_readwrite("name", &EnumSettingBits::name)
            .def_readwrite("options", &EnumSettingBits::options)
            .def("get_options", &EnumSettingBits::get_options)
            .def_property("defval", &EnumSettingBits::get_defval, &EnumSettingBits::set_defval)
            .def("get_value", &EnumSettingBits::get_value)
            .def("set_value", &EnumSettingBits::set_value);

    class_<FixedConnection>(m, "FixedConnection")
            .def(init<>())
            .def_readwrite("source", &FixedConnection::source)
            .def_readwrite("sink", &FixedConnection::sink);

    py::bind_vector<vector<FixedConnection>>(m, "FixedConnectionVector");

    class_<TileBitDatabase, shared_ptr<TileBitDatabase>>(m, "TileBitDatabase")
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

    class_<StringBoolPair>(m, "StringBoolPair")
            .def_readonly("first", &StringBoolPair::first)
            .def_readonly("second", &StringBoolPair::second);

    py::bind_vector<vector<StringBoolPair>>(m, "StringBoolPairVector");

    // From TileConfig.hpp
    class_<ConfigArc>(m, "ConfigArc")
            .def_readwrite("source", &ConfigArc::source)
            .def_readwrite("sink", &ConfigArc::sink);
    class_<ConfigWord>(m, "ConfigWord")
            .def_readwrite("name", &ConfigWord::name)
            .def_readwrite("value", &ConfigWord::value);
    class_<ConfigEnum>(m, "ConfigEnum")
            .def_readwrite("name", &ConfigEnum::name)
            .def_readwrite("value", &ConfigEnum::value);
    class_<ConfigUnknown>(m, "ConfigUnknown")
            .def_readwrite("frame", &ConfigUnknown::frame)
            .def_readwrite("bit", &ConfigUnknown::bit);

    py::bind_vector<vector<ConfigArc>>(m, "ConfigArcVector");
    py::bind_vector<vector<ConfigWord>>(m, "ConfigWordVector");
    py::bind_vector<vector<ConfigEnum>>(m, "ConfigEnumVector");
    py::bind_vector<vector<ConfigUnknown>>(m, "ConfigUnknownVector");

    class_<TileConfig>(m, "TileConfig")
            .def(init<>())
            .def_readwrite("carcs", &TileConfig::carcs)
            .def_readwrite("cwords", &TileConfig::cwords)
            .def_readwrite("cenums", &TileConfig::cenums)
            .def_readwrite("cunknowns", &TileConfig::cunknowns)
            .def("add_arc", &TileConfig::add_arc)
            .def("add_enum", &TileConfig::add_enum)
            .def("add_word", &TileConfig::add_word)
            .def("add_unknown", &TileConfig::add_unknown)
            .def("to_string", &TileConfig::to_string)
            .def_static("from_string", &TileConfig::from_string);

    // From ChipConfig.hpp
    py::bind_map<map<string, TileConfig>>(m, "TileConfigMap");
    py::bind_vector<vector<uint16_t>>(m, "Uint16Vector");
    py::bind_map<map<uint16_t, vector<uint16_t>>>(m, "Uint16VMap");

    class_<ChipConfig>(m, "ChipConfig")
            .def_readwrite("chip_name", &ChipConfig::chip_name)
            .def_readwrite("chip_variant", &ChipConfig::chip_variant)
            .def_readwrite("metadata", &ChipConfig::metadata)
            .def_readwrite("tiles", &ChipConfig::tiles)
            .def_readwrite("tilegroups", &ChipConfig::tilegroups)
            .def_readwrite("bram_data", &ChipConfig::bram_data)
            .def("to_string", &ChipConfig::to_string)
            .def_static("from_string", &ChipConfig::from_string)
            .def("to_chip", &ChipConfig::to_chip)
            .def_static("from_chip", &ChipConfig::from_chip);

    // From RoutingGraph.hpp
    class_<Location>(m, "Location")
            .def(init<int, int>())
            .def_readwrite("x", &Location::x)
            .def_readwrite("y", &Location::y)
            .def(self + self)
            .def(self == self)
            .def(self != self);

    class_<RoutingId>(m, "RoutingId")
            .def_readwrite("loc", &RoutingId::loc)
            .def_readwrite("id", &RoutingId::id)
            .def(self == self)
            .def(self != self);

    py::bind_vector<vector<RoutingId>>(m, "RoutingIdVector");

    class_<BelPin>(m, "BelPin")
            .def_readonly("bel", &BelPin::first)
            .def_readonly("pin", &BelPin::second);

    class_<BelWireDir>(m, "BelWireDir")
            .def_readonly("wire", &BelWireDir::first)
            .def_readonly("dir", &BelWireDir::second);

    enum_<PortDirection>(m, "PortDirection")
            .value("PORT_IN", PORT_IN)
            .value("PORT_OUT", PORT_OUT)
            .value("PORT_INOUT", PORT_INOUT);

    py::bind_vector<vector<BelPin>>(m, "BelPinVector");

    class_<RoutingWire>(m, "RoutingWire")
            .def_readwrite("id", &RoutingWire::id)
            .def_readwrite("uphill", &RoutingWire::uphill)
            .def_readwrite("downhill", &RoutingWire::downhill)
            .def_readwrite("belsUphill", &RoutingWire::belsUphill)
            .def_readwrite("belsDownhill", &RoutingWire::belsDownhill);

    class_<RoutingArc>(m, "RoutingArc")
            .def_readwrite("id", &RoutingArc::id)
            .def_readwrite("tiletype", &RoutingArc::tiletype)
            .def_readwrite("source", &RoutingArc::source)
            .def_readwrite("sink", &RoutingArc::sink)
            .def_readwrite("configurable", &RoutingArc::configurable);

    py::bind_map<map<ident_t, BelWireDir>>(m, "RoutingPinMap");

    class_<RoutingBel>(m, "RoutingBel")
            .def_readwrite("name", &RoutingBel::name)
            .def_readwrite("type", &RoutingBel::type)
            .def_readwrite("pins", &RoutingBel::pins)
            .def_readwrite("z", &RoutingBel::z);

    py::bind_map<map<ident_t, RoutingWire>>(m, "RoutingWireMap");

    py::bind_map<map<ident_t, RoutingArc>>(m, "RoutingArcMap");

    py::bind_map<map<ident_t, RoutingBel>>(m, "RoutingBelMap");

    class_<RoutingTileLoc>(m, "RoutingTileLoc")
            .def_readwrite("loc", &RoutingTileLoc::loc)
            .def_readwrite("wires", &RoutingTileLoc::wires)
            .def_readwrite("arcs", &RoutingTileLoc::arcs)
            .def_readwrite("bels", &RoutingTileLoc::bels);

    py::bind_map<map<Location, RoutingTileLoc>>(m, "RoutingTileMap");

    class_<RoutingGraph, shared_ptr<RoutingGraph>>(m, "RoutingGraph")
            .def_readonly("chip_name", &RoutingGraph::chip_name)
            .def_readonly("chip_family", &RoutingGraph::chip_family)
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
    class_<RelId>(m, "RelId")
            .def_readwrite("rel", &RelId::rel)
            .def_readwrite("id", &RelId::id)
            .def(self == self)
            .def(self != self);

    class_<BelPort>(m, "BelPort")
            .def_readwrite("bel", &BelPort::bel)
            .def_readwrite("pin", &BelPort::pin);
    class_<BelWire>(m, "BelWire")
            .def_readwrite("wire", &BelWire::wire)
            .def_readwrite("pin", &BelWire::pin)
            .def_readwrite("dir", &BelWire::dir);

    py::bind_vector<vector<BelPort>>(m, "BelPortVector");
    py::bind_vector<vector<BelWire>>(m, "BelWireVector");
    py::bind_vector<vector<RelId>>(m, "RelIdVector");
    class_<std::set<RelId>>(m, "RelIdSet")
        .def("__len__", [](const std::set<RelId> &v) { return v.size(); })
        .def("__iter__", [](std::set<RelId> &v) {
            return py::make_iterator(v.begin(), v.end());
        }, py::keep_alive<0, 1>()); /* Keep vector alive while iterator is used */

    enum_<ArcClass>(m, "ArcClass")
            .value("ARC_STANDARD", ARC_STANDARD)
            .value("ARC_FIXED", ARC_FIXED);
    class_<DdArcData>(m, "DdArcData")
            .def_readwrite("srcWire", &DdArcData::srcWire)
            .def_readwrite("sinkWire", &DdArcData::sinkWire)
            .def_readwrite("cls", &DdArcData::cls)
            .def_readwrite("delay", &DdArcData::delay)
            .def_readwrite("tiletype", &DdArcData::tiletype)
            .def_readwrite("lutperm_flags", &DdArcData::lutperm_flags);

    class_<WireData>(m, "WireData")
            .def_readwrite("name", &WireData::name)
            .def_readwrite("arcsDownhill", &WireData::arcsDownhill)
            .def_readwrite("arcsUphill", &WireData::arcsUphill)
            .def_readwrite("belPins", &WireData::belPins);

    class_<BelData>(m, "BelData")
            .def_readwrite("name", &BelData::name)
            .def_readwrite("type", &BelData::type)
            .def_readwrite("z", &BelData::z)
            .def_readwrite("wires", &BelData::wires);

    py::bind_vector<vector<BelData>>(m, "BelDataVector");
    py::bind_vector<vector<WireData>>(m, "WireDataVector");
    py::bind_vector<vector<DdArcData>>(m, "DdArcDataVector");

    class_<LocationData>(m, "LocationData")
            .def_readwrite("wires", &LocationData::wires)
            .def_readwrite("arcs", &LocationData::arcs)
            .def_readwrite("bels", &LocationData::bels)
            .def("checksum", &LocationData::checksum);

    py::bind_map<map<Location, checksum_t>>(m, "LocationMap");

    py::bind_map<map<checksum_t, LocationData>>(m, "LocationTypesMap");

    py::bind_map<map<Location, LocationData>>(m, "LocationMapDirect");

    class_<checksum_t>(m, "checksum_t")
            .def_readonly("first", &checksum_t::first)
            .def_readonly("second", &checksum_t::second)
            .def("key", [](const checksum_t &v) { return v; })
            .def(self == self);

    class_<DedupChipdb, shared_ptr<DedupChipdb>>(m, "DedupChipdb")
            .def_readwrite("locationTypes", &DedupChipdb::locationTypes)
            .def_readwrite("typeAtLocation", &DedupChipdb::typeAtLocation)
            .def("get_cs_data", &DedupChipdb::get_cs_data)
            .def("ident", &DedupChipdb::ident)
            .def("to_str", &DedupChipdb::to_str);

    m.def("make_dedup_chipdb", make_dedup_chipdb,
        py::arg("chip"), py::arg("include_lutperm_pips")=false, py::arg("split_slice_mode")=false);

    class_<OptimizedChipdb, shared_ptr<OptimizedChipdb>>(m, "OptimizedChipdb")
            .def_readwrite("tiles", &OptimizedChipdb::tiles)
            .def("ident", &OptimizedChipdb::ident)
            .def("to_str", &OptimizedChipdb::to_str);

    m.def("make_optimized_chipdb", make_optimized_chipdb);

}

#endif
