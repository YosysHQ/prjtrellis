#include "Chip.hpp"
#include "Tile.hpp"
#include "Database.hpp"
#include "Util.hpp"
#include "RoutingGraph.hpp"
#include "BitDatabase.hpp"
#include "Bels.hpp"
#include <algorithm>
#include <iostream>
using namespace std;

namespace Trellis {

Chip::Chip(string name) : Chip(get_chip_info(find_device_by_name(name)))
{}

Chip::Chip(string name, string variant) : Chip(get_chip_info(find_device_by_name_and_variant(name, variant)))
{}

Chip::Chip(uint32_t idcode) : Chip(get_chip_info(find_device_by_idcode(idcode)))
{}

Chip::Chip(const Trellis::ChipInfo &info) : info(info), cram(info.num_frames, info.bits_per_frame)
{
    vector<TileInfo> allTiles = get_device_tilegrid(DeviceLocator{info.family, info.name, info.variant});
    for (const auto &tile : allTiles) {
        tiles[tile.name] = make_shared<Tile>(tile, *this);
        int row, col;
        tie(row, col) = tile.get_row_col();
        tiles[tile.name]->row = row;
        tiles[tile.name]->col = col;
        if (int(tiles_at_location.size()) <= row) {
            tiles_at_location.resize(row+1);
        }
        if (int(tiles_at_location.at(row).size()) <= col) {
            tiles_at_location.at(row).resize(col+1);
        }
        tiles_at_location.at(row).at(col).push_back(make_pair(tile.name, tile.type));
    }

    if(info.family == "ECP5")
        global_data_ecp5 = get_global_info_ecp5(DeviceLocator{info.family, info.name, info.variant});
    else if(info.family == "MachXO") {} // No global routing
    else if (info.family == "MachXO2" || info.family == "MachXO3" || info.family == "MachXO3D")
        global_data_machxo2 = generate_global_info_machxo2();
    else
        throw runtime_error("Unknown chip family " + info.family);
}

shared_ptr<Tile> Chip::get_tile_by_name(string name)
{
    return tiles.at(name);
}

vector<shared_ptr<Tile>> Chip::get_tiles_by_position(int row, int col)
{
    vector<shared_ptr<Tile>> result;
    for (const auto &tile : tiles) {
        if (tile.second->row == row && tile.second->col == col)
            result.push_back(tile.second);
    }
    return result;
}

string Chip::get_tile_by_position_and_type(int row, int col, string type) {
    for (const auto &tile : tiles_at_location.at(row).at(col)) {
        if (tile.second == type)
            return tile.first;
    }
    throw runtime_error(fmt("no suitable tile found at R" << row << "C" << col));
}

string Chip::get_tile_by_position_and_type(int row, int col, set<string> type) {
    for (const auto &tile : tiles_at_location.at(row).at(col)) {
        if (type.find(tile.second) != type.end())
            return tile.first;
    }
    throw runtime_error(fmt("no suitable tile found at R" << row << "C" << col));
}


vector<shared_ptr<Tile>> Chip::get_tiles_by_type(string type)
{
    vector<shared_ptr<Tile>> result;
    for (const auto &tile : tiles) {
        if (tile.second->info.type == type)
            result.push_back(tile.second);
    }
    return result;
}

vector<shared_ptr<Tile>> Chip::get_all_tiles()
{
    vector<shared_ptr<Tile>> result;
    for (const auto &tile : tiles) {
        result.push_back(tile.second);
    }
    return result;
}

int Chip::get_max_row() const
{
    return info.max_row;
}

int Chip::get_max_col() const
{
    return info.max_col;
}

ChipDelta operator-(const Chip &a, const Chip &b)
{
    ChipDelta delta;
    for (const auto &tile : a.tiles) {
        CRAMDelta cd = tile.second->cram - b.tiles.at(tile.first)->cram;
        if (!cd.empty())
            delta[tile.first] = cd;
    }
    return delta;
}

shared_ptr<RoutingGraph> Chip::get_routing_graph(bool include_lutperm_pips, bool split_slice_mode)
{
    if(info.family == "ECP5") {
        return get_routing_graph_ecp5(include_lutperm_pips, split_slice_mode);
    } else if(info.family == "MachXO") {
        return get_routing_graph_machxo(include_lutperm_pips, split_slice_mode);
    } else if(info.family == "MachXO2" || info.family == "MachXO3" || info.family == "MachXO3D") {
        return get_routing_graph_machxo2(include_lutperm_pips, split_slice_mode);
    } else
      throw runtime_error("Unknown chip family: " + info.family);
}

shared_ptr<RoutingGraph> Chip::get_routing_graph_ecp5(bool include_lutperm_pips, bool split_slice_mode)
{
    shared_ptr<RoutingGraph> rg(new RoutingGraph(*this));
    //cout << "Building routing graph" << endl;
    for (auto tile_entry : tiles) {
        shared_ptr<Tile> tile = tile_entry.second;
        //cout << "    Tile " << tile->info.name << endl;
        shared_ptr<TileBitDatabase> bitdb = get_tile_bitdata(TileLocator{info.family, info.name, tile->info.type});
        bitdb->add_routing(tile->info, *rg);
        int x = tile->col;
        int y = tile->row;
        // SLICE Bels
        if (tile->info.type == "PLC2") {
            for (int z = 0; z < 4; z++) {
                if (split_slice_mode) {
                    for (int i = z*2; i < (z+1)*2; i++) {
                        CommonBels::add_logic_comb(*rg, x, y, i);
                        CommonBels::add_ff(*rg, x, y, i);
                    }
                } else {
                    CommonBels::add_lc(*rg, x, y, z);
                }
                if (include_lutperm_pips) {
                    // Add permutation pseudo-pips as a crossbar in front of each LUT's inputs
                    Location loc(x, y);
                    const string abcd = "ABCD";
                    for (int k = (z*2); k < ((z+1)*2); k++) {
                        for (int i = 0; i < 4; i++) {
                            for (int j = 0; j < 4; j++) {
                                if (i == j)
                                    continue;
                                string input = fmt(abcd[j] << k);
                                string output = fmt(abcd[i] << k << "_SLICE");
                                RoutingArc rarc;
                                rarc.id = rg->ident(fmt(input << "->" << output));
                                rarc.source = RoutingId{loc, rg->ident(input)};
                                rarc.sink = RoutingId{loc, rg->ident(output)};
                                rarc.tiletype = rg->ident(tile->info.type);
                                rarc.configurable = false;
                                rarc.lutperm_flags = (0x4000 | (k << 4) | ((i & 0x3) << 2) |(j & 0x3));
                                rg->add_arc(loc, rarc);
                            }
                        }
                    }
                }
            }
            if (split_slice_mode)
                CommonBels::add_ramw(*rg, x, y);
        }
        // PIO Bels
        if (tile->info.type.find("PICL0") != string::npos || tile->info.type.find("PICR0") != string::npos)
            for (int z = 0; z < 4; z++) {
                CommonBels::add_pio(*rg, x, y, z);
                Ecp5Bels::add_iologic(*rg, x, y, z, false);
            }
        if (tile->info.type.find("PIOT0") != string::npos || (tile->info.type.find("PICB0") != string::npos && tile->info.type != "SPICB0"))
            for (int z = 0; z < 2; z++) {
                CommonBels::add_pio(*rg, x, y, z);
                Ecp5Bels::add_iologic(*rg, x, y, z, true);
            }
        if (tile->info.type == "SPICB0") {
            CommonBels::add_pio(*rg, x, y, 0);
            Ecp5Bels::add_iologic(*rg, x, y, 0, true);
        }
        // DCC Bels
        if (tile->info.type == "LMID_0")
            for (int z = 0; z < 14; z++)
                Ecp5Bels::add_dcc(*rg, x, y, "L", std::to_string(z));
        if (tile->info.type == "RMID_0")
            for (int z = 0; z < 14; z++)
                Ecp5Bels::add_dcc(*rg, x, y, "R", std::to_string(z));
        if (tile->info.type == "TMID_0")
            for (int z = 0; z < 12; z++)
                Ecp5Bels::add_dcc(*rg, x, y, "T", std::to_string(z));
        if (tile->info.type == "BMID_0V" || tile->info.type == "BMID_0H")
            for (int z = 0; z < 16; z++)
                Ecp5Bels::add_dcc(*rg, x, y, "B", std::to_string(z));
        if (tile->info.type == "EBR_CMUX_UL" || tile->info.type == "DSP_CMUX_UL")
            Ecp5Bels::add_dcs(*rg, x, y, 0);
        if (tile->info.type == "EBR_CMUX_LL" || tile->info.type == "EBR_CMUX_LL_25K")
            Ecp5Bels::add_dcs(*rg, x, y, 1);
        // RAM Bels
        if (tile->info.type == "MIB_EBR0" || tile->info.type == "EBR_CMUX_UR" || tile->info.type == "EBR_CMUX_LR"
            || tile->info.type == "EBR_CMUX_LR_25K")
            Ecp5Bels::add_bram(*rg, x, y, 0);
        if (tile->info.type == "MIB_EBR2")
            Ecp5Bels::add_bram(*rg, x, y, 1);
        if (tile->info.type == "MIB_EBR4")
            Ecp5Bels::add_bram(*rg, x, y, 2);
        if (tile->info.type == "MIB_EBR6")
            Ecp5Bels::add_bram(*rg, x, y, 3);
        // DSP Bels
        if (tile->info.type == "MIB_DSP0")
            Ecp5Bels::add_mult18(*rg, x, y, 0);
        if (tile->info.type == "MIB_DSP1")
            Ecp5Bels::add_mult18(*rg, x, y, 1);
        if (tile->info.type == "MIB_DSP4")
            Ecp5Bels::add_mult18(*rg, x, y, 4);
        if (tile->info.type == "MIB_DSP5")
            Ecp5Bels::add_mult18(*rg, x, y, 5);
        if (tile->info.type == "MIB_DSP3")
            Ecp5Bels::add_alu54b(*rg, x, y, 3);
        if (tile->info.type == "MIB_DSP7")
            Ecp5Bels::add_alu54b(*rg, x, y, 7);
        // PLL Bels
        if (tile->info.type == "PLL0_UL")
            Ecp5Bels::add_pll(*rg, "UL", x+1, y);
        if (tile->info.type == "PLL0_LL")
            Ecp5Bels::add_pll(*rg, "LL", x, y-1);
        if (tile->info.type == "PLL0_LR")
            Ecp5Bels::add_pll(*rg, "LR", x, y-1);
        if (tile->info.type == "PLL0_UR")
            Ecp5Bels::add_pll(*rg, "UR", x-1, y);
        // DCU and ancillary Bels
        if (tile->info.type == "DCU0") {
            Ecp5Bels::add_dcu(*rg, x, y);
            Ecp5Bels::add_extref(*rg, x, y);
        }
        if (tile->info.type == "BMID_0H")
            for (int z = 0; z < 2; z++)
                Ecp5Bels::add_pcsclkdiv(*rg, x, y-1, z);
        // Config/system Bels
        if (tile->info.type == "EFB0_PICB0") {
            Ecp5Bels::add_misc(*rg, "GSR", x, y-1);
            Ecp5Bels::add_misc(*rg, "JTAGG", x, y-1);
            Ecp5Bels::add_misc(*rg, "OSCG", x, y-1);
            Ecp5Bels::add_misc(*rg, "SEDGA", x, y-1);
        }
        if (tile->info.type == "DTR")
            Ecp5Bels::add_misc(*rg, "DTR", x, y-1);
        if (tile->info.type == "EFB1_PICB1")
            Ecp5Bels::add_misc(*rg, "USRMCLK", x-5, y);
        if (tile->info.type == "ECLK_L") {
            Ecp5Bels::add_ioclk_bel(*rg, "CLKDIVF", x-2, y, 0, 7);
            Ecp5Bels::add_ioclk_bel(*rg, "CLKDIVF", x-2, y, 1, 6);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x-2, y, 0, 7);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x-2, y, 1, 7);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x-2, y+1, 0, 6);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x-2, y+1, 1, 6);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x-2, y, 0, 7);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x-2, y, 1, 7);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x-2, y+1, 0, 6);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x-2, y+1, 1, 6);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x-2, y-1, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x-2, y, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x-2, y+1, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x-2, y+2, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKBRIDGECS", x-2, y, 1);
            Ecp5Bels::add_ioclk_bel(*rg, "BRGECLKSYNC", x-2, y, 1);
        }
        if (tile->info.type == "ECLK_R") {
            Ecp5Bels::add_ioclk_bel(*rg, "CLKDIVF", x+2, y, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "CLKDIVF", x+2, y, 1);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x+2, y, 0, 2);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x+2, y, 1, 2);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x+2, y+1, 0, 3);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKSYNCB", x+2, y+1, 1, 3);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x+2, y, 0, 2);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x+2, y, 1, 2);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x+2, y+1, 0, 3);
            Ecp5Bels::add_ioclk_bel(*rg, "TRELLIS_ECLKBUF", x+2, y+1, 1, 3);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x+2, y-1, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x+2, y, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x+2, y+1, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "DLLDELD", x+2, y+2, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "ECLKBRIDGECS", x+2, y, 0);
            Ecp5Bels::add_ioclk_bel(*rg, "BRGECLKSYNC", x+2, y, 0);
        }
        if (tile->info.type == "DDRDLL_UL")
            Ecp5Bels::add_ioclk_bel(*rg, "DDRDLL", x-2, y-10, 0);
        if (tile->info.type == "DDRDLL_ULA")
            Ecp5Bels::add_ioclk_bel(*rg, "DDRDLL", x-2, y-13, 0);
        if (tile->info.type == "DDRDLL_UR")
            Ecp5Bels::add_ioclk_bel(*rg, "DDRDLL", x+2, y-10, 0);
        if (tile->info.type == "DDRDLL_URA")
            Ecp5Bels::add_ioclk_bel(*rg, "DDRDLL", x+2, y-13, 0);
        if (tile->info.type == "DDRDLL_LL")
            Ecp5Bels::add_ioclk_bel(*rg, "DDRDLL", x-2, y+13, 0);
        if (tile->info.type == "DDRDLL_LR")
            Ecp5Bels::add_ioclk_bel(*rg, "DDRDLL", x+2, y+13, 0);
        if (tile->info.type == "PICL0_DQS2" || tile->info.type == "PICR0_DQS2")
            Ecp5Bels::add_ioclk_bel(*rg, "DQSBUFM", x, y, 0);

    }
    return rg;
}

shared_ptr<RoutingGraph> Chip::get_routing_graph_machxo2(bool include_lutperm_pips, bool split_slice_mode)
{
    shared_ptr<RoutingGraph> rg(new RoutingGraph(*this));

    for (auto tile_entry : tiles) {
        shared_ptr<Tile> tile = tile_entry.second;
        //cout << "    Tile " << tile->info.name << endl;
        shared_ptr<TileBitDatabase> bitdb = get_tile_bitdata(TileLocator{info.family, info.name, tile->info.type});
        bitdb->add_routing(tile->info, *rg);
        int x = tile->col;
        int y = tile->row;

        // SLICE Bels
        if (tile->info.type == "PLC") {
            for (int z = 0; z < 4; z++) {
                if (split_slice_mode) {
                    for (int i = z*2; i < (z+1)*2; i++) {
                        CommonBels::add_logic_comb(*rg, x, y, i);
                        CommonBels::add_ff(*rg, x, y, i);
                    }
                } else {
                    CommonBels::add_lc(*rg, x, y, z);
                }
                if (include_lutperm_pips) {
                    // Add permutation pseudo-pips as a crossbar in front of each LUT's inputs
                    Location loc(x, y);
                    const string abcd = "ABCD";
                    for (int k = (z*2); k < ((z+1)*2); k++) {
                        for (int i = 0; i < 4; i++) {
                            for (int j = 0; j < 4; j++) {
                                if (i == j)
                                    continue;
                                string input = fmt(abcd[j] << k);
                                string output = fmt(abcd[i] << k << "_SLICE");
                                RoutingArc rarc;
                                rarc.id = rg->ident(fmt(input << "->" << output));
                                rarc.source = RoutingId{loc, rg->ident(input)};
                                rarc.sink = RoutingId{loc, rg->ident(output)};
                                rarc.tiletype = rg->ident(tile->info.type);
                                rarc.configurable = false;
                                rarc.lutperm_flags = (0x4000 | (k << 4) | ((i & 0x3) << 2) |(j & 0x3));
                                rg->add_arc(loc, rarc);
                            }
                        }
                    }
                }
            }
            if (split_slice_mode)
                CommonBels::add_ramw(*rg, x, y);
        }
        // PIO Bels
        // DUMMY and CIB tiles can have the below strings and can possibly
        // have BELs. But they will not have PIO BELs.
        if (tile->info.type.find("DUMMY") == string::npos && tile->info.type.find("CIB") == string::npos && tile->info.type.find("PIC") != string::npos) {
            
            // Single I/O pair.
            if (tile->info.type.find("LS0") != string::npos || tile->info.type.find("RS0") != string::npos ||
                tile->info.type.find("BS0") != string::npos || tile->info.type.find("TS0") != string::npos ||
                tile->info.type.find("LLC0PIC") != string::npos) {
                for (int z = 0; z < 2; z++)
                    CommonBels::add_pio(*rg, x, y, z);
            } else {
                for (int z = 0; z < 4; z++)
                    CommonBels::add_pio(*rg, x, y, z);
            }
        }

        // DCC/DCM Bels
        if (tile->info.type.find("CENTER_EBR_CIB") != string::npos) {
          for (int z = 0; z < 8; z++)
              MachXO2Bels::add_dcc(*rg, x, y, z);
          for (int z = 6; z < 8; z++)
              // Start at z = 8, but names start at 6.
              MachXO2Bels::add_dcm(*rg, x, y, z, z + 2);
        }

        if (tile->info.type.find("CIB_CFG0") != string::npos) {
            MachXO2Bels::add_osch(*rg, x, y, 0);
        }
    }

    return rg;
}

shared_ptr<RoutingGraph> Chip::get_routing_graph_machxo(bool include_lutperm_pips, bool split_slice_mode)
{
    shared_ptr<RoutingGraph> rg(new RoutingGraph(*this));
    for (auto tile_entry : tiles) {
        shared_ptr<Tile> tile = tile_entry.second;
        //cout << "    Tile " << tile->info.name << endl;
        shared_ptr<TileBitDatabase> bitdb = get_tile_bitdata(TileLocator{info.family, info.name, tile->info.type});
        bitdb->add_routing(tile->info, *rg);
        int x = tile->col;
        int y = tile->row;

        // SLICE Bels
        if (tile->info.type == "PLC") {
            for (int z = 0; z < 4; z++) {
                if (split_slice_mode) {
                    for (int i = z*2; i < (z+1)*2; i++) {
                        CommonBels::add_logic_comb(*rg, x, y, i);
                        CommonBels::add_ff(*rg, x, y, i);
                    }
                } else {
                    CommonBels::add_lc(*rg, x, y, z);
                }
                if (include_lutperm_pips) {
                    // Add permutation pseudo-pips as a crossbar in front of each LUT's inputs
                    Location loc(x, y);
                    const string abcd = "ABCD";
                    for (int k = (z*2); k < ((z+1)*2); k++) {
                        for (int i = 0; i < 4; i++) {
                            for (int j = 0; j < 4; j++) {
                                if (i == j)
                                    continue;
                                string input = fmt(abcd[j] << k);
                                string output = fmt(abcd[i] << k << "_SLICE");
                                RoutingArc rarc;
                                rarc.id = rg->ident(fmt(input << "->" << output));
                                rarc.source = RoutingId{loc, rg->ident(input)};
                                rarc.sink = RoutingId{loc, rg->ident(output)};
                                rarc.tiletype = rg->ident(tile->info.type);
                                rarc.configurable = false;
                                rarc.lutperm_flags = (0x4000 | (k << 4) | ((i & 0x3) << 2) |(j & 0x3));
                                rg->add_arc(loc, rarc);
                            }
                        }
                    }
                }
            }
            if (split_slice_mode)
                CommonBels::add_ramw(*rg, x, y);
        }
        // TODO:FSLICE Bels

        // PIO Bels
        if (tile->info.type.find("PIC2") != string::npos) {
            for (int z = 0; z < 2; z++)
                CommonBels::add_pio(*rg, x, y, z);
        } else if (tile->info.type.find("PIC4") != string::npos ||
                   tile->info.type.find("PIC_L") != string::npos ||
                   tile->info.type.find("PIC_R") != string::npos) {
            for (int z = 0; z < 4; z++)
                CommonBels::add_pio(*rg, x, y, z);
        } else if (tile->info.type.find("PIC6") != string::npos) {
            for (int z = 0; z < 6; z++)
                CommonBels::add_pio(*rg, x, y, z);
        }
    }
    return rg;
}

// Global network funcs

bool GlobalRegion::matches(int row, int col) const {
    return (row >= y0 && row <= y1 && col >= x0 && col <= x1);
}

bool TapSegment::matches_left(int row, int col) const {
    UNUSED(row);
    return (col >= lx0 && col <= lx1);
}

bool TapSegment::matches_right(int row, int col) const {
    UNUSED(row);
    return (col >= rx0 && col <= rx1);
}

string Ecp5GlobalsInfo::get_quadrant(int row, int col) const {
    for (const auto &quad : quadrants) {
        if (quad.matches(row, col))
            return quad.name;
    }
    throw runtime_error(fmt("R" << row << "C" << col << " matches no globals quadrant"));
}

TapDriver Ecp5GlobalsInfo::get_tap_driver(int row, int col) const {
    for (const auto &seg : tapsegs) {
        if (seg.matches_left(row, col)) {
            TapDriver td;
            td.dir = TapDriver::LEFT;
            td.col = seg.tap_col;
            return td;
        }
        if (seg.matches_right(row, col)) {
            TapDriver td;
            td.dir = TapDriver::RIGHT;
            td.col = seg.tap_col;
            return td;
        }
    }
    throw runtime_error(fmt("R" << row << "C" << col << " matches no global TAP_DRIVE segment"));
}

pair<int, int> Ecp5GlobalsInfo::get_spine_driver(std::string quadrant, int col) {
    for (const auto &seg : spinesegs) {
        if (seg.quadrant == quadrant && seg.tap_col == col) {
            return make_pair(seg.spine_row, seg.spine_col);
        }
    }
    throw runtime_error(fmt(quadrant << "C" << col << " matches no global SPINE segment"));
}

map<pair<int, int>, int> start_stride = {
    // LCMXO2-256
    {make_pair(7, 9), 0}, // (0, 4)
    // LCMXO2-640
    {make_pair(8, 17), 1}, // (1, 5)
    // LCMXO2-1200, LCMXO3-1300
    {make_pair(12, 21),0}, // (0, 4)
    // LCMXO2-2000, LCMXO3-2100
    {make_pair(15, 25), 3}, // (3, 7)
    // LCMXO2-4000, LCMXO3-4300
    {make_pair(22, 31), 1}, // (1, 5)
    // LCMXO2-7000, LCMXO3-6900
    {make_pair(27, 40), 2}, // (2, 6)
    // LCMXO3-9400
    {make_pair(31, 48), 0}, // (0, 4)
};

MachXO2GlobalsInfo Chip::generate_global_info_machxo2()
{
    MachXO2GlobalsInfo data;
    int stride = start_stride[make_pair(info.max_row, info.max_col)];
    // At column zero, always 6 wires, that do not
    // match those in column 1
    std::vector<int> items_col_0;
    for (int i=0;i<4;i++) {
        if (i!=stride) {
            items_col_0.push_back(i);
            items_col_0.push_back(i + 4);
        }
    }
    data.ud_conns.push_back(items_col_0);

    // For the rest of columns
    for(int i=1; i < info.max_col; i++)
    {
        std::vector<int> items;
        items.push_back(stride);
        items.push_back(stride + 4);
        stride = (stride + 1) & 3;
        data.ud_conns.push_back(items);
    }

    // Last one have 4 wires
    std::vector<int> items_col_last;
    items_col_last.push_back(stride);
    items_col_last.push_back(stride + 4);
    stride = (stride + 1) & 3;
    items_col_last.push_back(stride);
    items_col_last.push_back(stride + 4);
    data.ud_conns.push_back(items_col_last);
    return data;
}

}
