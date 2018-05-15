#include "Bitstream.hpp"
#include "Chip.hpp"
#include "Database.hpp"
#include "Tile.hpp"
#include "BitDatabase.hpp"
#include "TileConfig.hpp"

#include <vector>
#include <string>
#include <iostream>

#include <boost/python.hpp>

#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>
#include <boost/python/exception_translator.hpp>

using namespace boost::python;
using namespace Trellis;


void translate_bspe(const BitstreamParseError &e) {
    // Use the Python 'C' API to set up an exception object
    PyErr_SetString(PyExc_ValueError, e.what());
}


BOOST_PYTHON_MODULE (pytrellis) {
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
            .def("deserialise_chip", &Bitstream::deserialise_chip);

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
            .def_readonly("pad_bits_after_frame", &ChipInfo::pad_bits_after_frame);

    class_<map<string, shared_ptr<Tile>>>("TileMap")
            .def(map_indexing_suite<map<string, shared_ptr<Tile>>, true>());

    class_<vector<shared_ptr<Tile>>>("TileVector")
            .def(vector_indexing_suite<vector<shared_ptr<Tile>>, true>());

    class_<Chip>("Chip", init<string>())
            .def(init<uint32_t>())
            .def(init<const ChipInfo &>())
            .def("get_tile_by_name", &Chip::get_tile_by_name)
            .def("get_tiles_by_position", &Chip::get_tiles_by_position)
            .def("get_tiles_by_type", &Chip::get_tiles_by_type)
            .def_readonly("info", &Chip::info)
            .def_readwrite("cram", &Chip::cram)
            .def_readwrite("tiles", &Chip::tiles)
            .def_readwrite("usercode", &Chip::usercode)
            .def_readwrite("metadata", &Chip::metadata)
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
            .def_readwrite("cram", &Tile::cram);

    // From Database.cpp
    def("load_database", load_database);
    def("find_device_by_name", find_device_by_name);
    def("find_device_by_idcode", find_device_by_idcode);
    def("get_chip_info", get_chip_info);
    def("get_device_tilegrid", get_device_tilegrid);
    def("get_tile_bitdata", get_tile_bitdata);

    // From BitDatabase.cpp
    class_<ConfigBit>("ConfigBit")
            .def_readwrite("frame", &ConfigBit::frame)
            .def_readwrite("bit", &ConfigBit::bit)
            .def_readwrite("inv", &ConfigBit::inv);

    def("cbit_from_str", cbit_from_str);
    class_<vector<ConfigBit>>("ConfigBitVector")
            .def(vector_indexing_suite<vector<ConfigBit>>());

    class_<BitGroup>("BitGroup")
            .def_readwrite("bits", &BitGroup::bits)
            .def("match", &BitGroup::match)
            .def("add_coverage", &BitGroup::add_coverage)
            .def("set_group", &BitGroup::set_group)
            .def("clear_group", &BitGroup::clear_group);

    class_<ArcData>("ArcData")
            .def_readwrite("source", &ArcData::source)
            .def_readwrite("sink", &ArcData::sink)
            .def_readwrite("bits", &ArcData::bits);

    class_<vector<ArcData>>("ArcDataVector")
            .def(vector_indexing_suite<vector<ArcData>>());

    class_<MuxBits>("MuxBits")
            .def_readwrite("sink", &MuxBits::sink)
            .def_readwrite("arcs", &MuxBits::arcs)
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
            .def_readwrite("defval", &EnumSettingBits::defval)
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
            .def("add_mux", &TileBitDatabase::add_mux)
            .def("add_setting_word", &TileBitDatabase::add_setting_word)
            .def("add_setting_enum", &TileBitDatabase::add_setting_enum)
            .def("add_fixed_conn", &TileBitDatabase::add_fixed_conn)
            .def("save", &TileBitDatabase::save);

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
            .def_readwrite("cunknowns", &TileConfig::cunknowns);
}
