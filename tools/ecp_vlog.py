import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable, ClassVar, Dict, List, Optional, Sequence, Set, Tuple, Type

try:
    # optional import to get natural sorting of integers (i.e. 1, 5, 9, 10 instead of 1, 10, 5, 9)
    from natsort import natsorted
except ImportError:
    natsorted = sorted

import pytrellis
import database


# Conversions between tiles and locations
@dataclass
class TileData:
    tile: pytrellis.Tile
    cfg: pytrellis.TileConfig


Location = Tuple[int, int]  # pytrellis.Location cannot be used as a dictionary key
TilesByLoc = Dict[Location, List[TileData]]


def make_tiles_by_loc(chip: pytrellis.Chip) -> TilesByLoc:
    tiles_by_loc: TilesByLoc = defaultdict(list)

    for tilename, tile in chip.tiles.items():
        locator = pytrellis.TileLocator(chip.info.family, chip.info.name, tile.info.type)
        tilebitdb = pytrellis.get_tile_bitdata(locator)
        tilecfg = tilebitdb.tile_cram_to_config(tile.cram)

        rc = tile.info.get_row_col()
        row, col = rc.first, rc.second
        tileloc = pytrellis.Location(col, row)

        tiles_by_loc[tileloc.x, tileloc.y].append(TileData(tile, tilecfg))

    return tiles_by_loc


# Utility classes representing a graph of configured connections
@dataclass(eq=True, order=True, frozen=True)
class Ident:
    """ An identifier in the routing graph """

    # place label first so we sort by identifier
    label: str = field(compare=False)
    # Idents are unique by ID so we only need to compare IDs
    id: int = field(repr=False)
    # Having a cache for Ident objects reduces memory pressure,
    # speeds up Ident creation slightly, and significantly reduces
    # the size of pickled graphs.
    _cache: ClassVar[Dict[int, "Ident"]] = {}

    @classmethod
    def from_id(cls, rgraph: pytrellis.RoutingGraph, id: int) -> "Ident":
        if id in cls._cache:
            return cls._cache[id]
        inst = Ident(rgraph.to_str(id), id)
        cls._cache[id] = inst
        return inst

    @classmethod
    def from_label(cls, rgraph: pytrellis.RoutingGraph, label: str) -> "Ident":
        return cls.from_id(rgraph, rgraph.ident(label))

    def __str__(self) -> str:
        return self.label


@dataclass(eq=True, order=True, frozen=True)
class Node:
    """ A node in the routing graph - either a wire or a BEL pin """

    # put y first so we sort by row, then column
    y: int
    x: int
    id: Ident
    pin: Optional[Ident] = None
    mod_name_map: ClassVar[Optional[Dict[str, str]]] = None

    @property
    def loc(self) -> pytrellis.Location:
        return pytrellis.Location(self.x, self.y)

    @property
    def mod_name(self) -> str:
        res = f"R{self.y}C{self.x}_{self.name}"
        if self.mod_name_map:
            return self.mod_name_map.get(res, res)
        return res

    @property
    def name(self) -> str:
        return self.id.label

    @property
    def pin_name(self) -> str:
        if self.pin is None:
            return ""
        return self.pin.label

    def __str__(self) -> str:
        res = self.mod_name
        if self.pin is not None:
            res += "$" + self.pin_name
        return res


EdgeMap = Dict[Node, Set[Node]]


@dataclass
class Component:
    graph: "ConnectionGraph"
    nodes: Set[Node] = field(default_factory=set)

    def get_roots(self) -> Set[Node]:
        roots = set()
        seen: Dict[Node, int] = {}

        def visit(node: Node) -> None:
            if node in seen:
                if seen[node] == 0:
                    print(f"Warning: node {node} is part of a cycle!")
                return
            seen[node] = 0
            if not self.graph.edges_rev[node]:
                roots.add(node)
            else:
                for x in self.graph.edges_rev[node]:
                    visit(x)
            seen[node] = 1

        for x in self.nodes:
            visit(x)

        return roots

    def get_leaves(self) -> Set[Node]:
        leaves = set()
        seen: Dict[Node, int] = {}

        def visit(node: Node) -> None:
            if node in seen:
                if seen[node] == 0:
                    print(f"Warning: node {node} is part of a cycle!")
                return
            seen[node] = 0
            if not self.graph.edges_fwd[node]:
                leaves.add(node)
            else:
                for x in self.graph.edges_fwd[node]:
                    visit(x)
            seen[node] = 1

        for x in self.nodes:
            visit(x)

        return leaves


@dataclass
class ConnectionGraph:
    """ A directed graph of Nodes. """

    edges_fwd: EdgeMap = field(default_factory=lambda: defaultdict(set))
    edges_rev: EdgeMap = field(default_factory=lambda: defaultdict(set))

    def add_edge(self, source: Node, sink: Node) -> None:
        self.edges_fwd[source].add(sink)
        self.edges_rev[sink].add(source)

    def get_components(self) -> List[Component]:
        seen: Set[Node] = set()

        def visit(node: Node, component: Component) -> None:
            if node in seen:
                return
            seen.add(node)

            component.nodes.add(node)
            if node in self.edges_fwd:
                for x in self.edges_fwd[node]:
                    visit(x, component)
            if node in self.edges_rev:
                for x in self.edges_rev[node]:
                    visit(x, component)

        components: List[Component] = []
        for edges in (self.edges_rev, self.edges_fwd):
            for node in edges:
                if node in seen:
                    continue
                component = Component(self)
                visit(node, component)
                components.append(component)

        return components


# Connection graph generation
def gen_config_graph(chip: pytrellis.Chip, rgraph: pytrellis.RoutingGraph, tiles_by_loc: TilesByLoc) -> ConnectionGraph:
    @lru_cache(None)
    def get_zero_bit_arcs(chip: pytrellis.Chip, tiletype: str) -> Dict[str, List[str]]:
        """Get configurable zero-bit arcs from the given tile.

        tile_cram_to_config ignores zero-bit arcs when generating the TileConfig,
        which means that if all bits are unset for a given mux, no connection is
        generated at all."""
        locator = pytrellis.TileLocator(chip.info.family, chip.info.name, tiletype)
        tilebitdb = pytrellis.get_tile_bitdata(locator)
        arcs: Dict[str, List[str]] = defaultdict(list)
        for sink in tilebitdb.get_sinks():
            mux_data = tilebitdb.get_mux_data_for_sink(sink)
            for arc_name, arc_data in mux_data.arcs.items():
                if len(arc_data.bits.bits) == 0:
                    arcs[sink].append(arc_name)
        return arcs

    def bel_to_node(pos: Tuple[pytrellis.RoutingId, int]) -> Node:
        rid, bel_pin = pos
        id = Ident.from_id(rgraph, rid.id)
        pin = Ident.from_id(rgraph, bel_pin)
        return Node(x=rid.loc.x, y=rid.loc.y, id=id, pin=pin)

    def wire_to_node(rid: pytrellis.RoutingId) -> Node:
        id = Ident.from_id(rgraph, rid.id)
        return Node(x=rid.loc.x, y=rid.loc.y, id=id)

    config_graph = ConnectionGraph()

    for loc in tiles_by_loc:
        rtile = rgraph.tiles[pytrellis.Location(loc[0], loc[1])]
        for tiledata in tiles_by_loc[loc]:
            tile = tiledata.tile
            for arc in tiledata.cfg.carcs:
                rarc = rtile.arcs[rgraph.ident(f"{arc.source}->{arc.sink}")]
                sourcenode = wire_to_node(rarc.source)
                sinknode = wire_to_node(rarc.sink)
                config_graph.add_edge(sourcenode, sinknode)

    # Expand configuration arcs to include BEL connections and zero-bit arcs
    arc_graph = ConnectionGraph()
    nodes_seen: Set[Node] = set()

    def visit_node(node: Node, bel_func: Callable[[Node], None]) -> None:
        """ Add unconfigurable or implicit arcs to the given node """
        if node in nodes_seen:
            return
        nodes_seen.add(node)

        try:
            rtile = rgraph.tiles[node.loc]
            rwire = rtile.wires[node.id.id]
        except KeyError:
            # there's a handful of troublesome cases which are outside of my control.
            # Example: R0C31_G_ULDDRDEL does not exist; it's actually supposed to be the "fixed"
            # connection G_ULDDRDEL=>DDRDEL but G_ULDDRDEL is not in the same tile.
            print(f"Error: failed to find node {str(node)}", file=sys.stderr)
            return

        if node not in config_graph.edges_rev:
            # Not configured - possible zero-bit configuration
            for tiledata in tiles_by_loc[node.x, node.y]:
                arcs = get_zero_bit_arcs(chip, tiledata.tile.info.type)
                sources = arcs.get(node.id.label, [])
                if not sources:
                    continue
                for source in sources:
                    sourceid = Ident.from_label(rgraph, source)
                    sourcenode = Node(x=node.x, y=node.y, id=sourceid)
                    arc_graph.add_edge(sourcenode, node)
                    visit_node(sourcenode, bel_func)

        # Add fixed connections
        for bel in rwire.belsUphill:
            arc_graph.add_edge(bel_to_node(bel), node)
            bel_func(wire_to_node(bel[0]))
        for bel in rwire.belsDownhill:
            arc_graph.add_edge(node, bel_to_node(bel))
            bel_func(wire_to_node(bel[0]))
        for routes in [rwire.uphill, rwire.downhill]:
            for rarcrid in routes:
                rarcname = rgraph.to_str(rarcrid.id)
                if "=>" in rarcname:
                    # => means a fixed (unconfigurable) connection
                    rarc = rgraph.tiles[rarcrid.loc].arcs[rarcrid.id]
                    sourcenode = wire_to_node(rarc.source)
                    sinknode = wire_to_node(rarc.sink)
                    arc_graph.add_edge(sourcenode, sinknode)
                    visit_node(sourcenode, bel_func)
                    visit_node(sinknode, bel_func)

        # Add global (clock) connections - Project Trellis omits a lot of these :(
        if node.name.startswith("G_HPBX"):
            # TAP_DRIVE -> PLB tile
            tap = chip.global_data.get_tap_driver(node.y, node.x)
            if tap.dir == pytrellis.TapDir.LEFT:
                tap_name = node.name.replace("G_HPBX", "L_HPBX")
            else:
                tap_name = node.name.replace("G_HPBX", "R_HPBX")
            tap_id = Ident.from_label(rgraph, tap_name)
            tap_node = Node(x=tap.col, y=node.y, id=tap_id)
            arc_graph.add_edge(tap_node, node)
            visit_node(tap_node, bel_func)

        elif node.name.startswith("G_VPTX"):
            # Spine tile -> TAP_DRIVE
            tap = chip.global_data.get_tap_driver(node.y, node.x)
            if tap.col == node.x:
                # Spine output
                quadrant = chip.global_data.get_quadrant(node.y, node.x)
                spine = chip.global_data.get_spine_driver(quadrant, node.x)
                spine_node = Node(x=spine.second, y=spine.first, id=node.id)
                arc_graph.add_edge(spine_node, node)
                visit_node(spine_node, bel_func)

        elif node.name.startswith("G_HPRX"):
            # Center mux -> spine tile (qqPCLKn -> G_HPRXnn00)
            quadrant = chip.global_data.get_quadrant(node.y, node.x)
            assert node.name.endswith("00")
            clkid = int(node.name[6:-2])
            global_id = Ident.from_label(rgraph, f"G_{quadrant}PCLK{clkid}")
            global_node = Node(x=0, y=0, id=global_id)
            arc_graph.add_edge(global_node, node)
            visit_node(global_node, bel_func)

    # Visit every configured arc and record all BELs seen
    bels_todo: Set[Node] = set()
    for sourcenode, nodes in config_graph.edges_fwd.items():
        for sinknode in nodes:
            arc_graph.add_edge(sourcenode, sinknode)
            visit_node(sourcenode, bels_todo.add)
            visit_node(sinknode, bels_todo.add)

    # Adding *every* fixed connection is too expensive.
    # As a compromise, add any fixed connection connected
    # to used BELs. Ignore BELs that don't have any configured
    # arcs.
    for node in bels_todo:
        rtile = rgraph.tiles[node.loc]
        for _, rwire in rtile.wires.items():
            wireident = Ident.from_id(rgraph, rwire.id)
            wirenode = Node(x=node.x, y=node.y, id=wireident)
            for bel in rwire.belsUphill:
                if bel[0].id == node.id.id:
                    arc_graph.add_edge(bel_to_node(bel), wirenode)
                    visit_node(wirenode, lambda node: None)
            for bel in rwire.belsDownhill:
                if bel[0].id == node.id.id:
                    arc_graph.add_edge(wirenode, bel_to_node(bel))
                    visit_node(wirenode, lambda node: None)

    return arc_graph


# Verilog generation
def filter_node(node: Node) -> bool:
    if node.pin is None:
        # This is a bit extreme, but we assume that all *useful* wires
        # go between BELs.
        return False
    if node.pin_name.startswith("IOLDO") or node.pin_name.startswith("IOLTO"):
        # IOLDO/IOLTO are for internal use:
        # https://freenode.irclog.whitequark.org/~h~openfpga/2018-12-25#23748701;
        # 07:55 <daveshah> kbeckmann: IOLDO and IOLTO are for internal use only
        # 07:55 <daveshah> They are for the dedicated interconnect between IOLOGIC and PIO
        return False
    if node.pin_name == "INDD":
        # I don't know what this pin is, but it often appears to be connected to $DI.
        # Disabling it because sometimes it ends up in a multi-root configuration with PIO$O,
        # which makes it (probably) redundant?
        return False
    return True


@dataclass
class Module:
    """ A class to encapsulate a synthesized BEL supported by simulation """

    module_name: str
    tiledata: TileData
    pin_map: Dict[str, Node]

    input_pins: ClassVar[List[str]] = []
    output_pins: ClassVar[List[str]] = []

    @classmethod
    def create_from_node(cls, node: Node, tiles_by_loc: TilesByLoc) -> Optional["Module"]:
        modcls: Type[Module]
        if node.name.startswith("SLICE"):
            modcls = SliceModule
            tiletype = "PLC2"
        elif node.name.startswith("EBR"):
            modcls = EBRModule
            tiletype = "MIB_EBR"
        else:
            return None

        for tiledata in tiles_by_loc[node.x, node.y]:
            if tiledata.tile.info.type.startswith(tiletype):
                break
        else:
            raise Exception(f"Tile type {tiletype} not found for node {node}")

        return modcls(node.name, tiledata, {})

    @classmethod
    def print_definition(cls) -> None:
        """ Print the Verilog code for the module definition """
        raise NotImplementedError()

    def _print_parameters(self, param_renames: Dict[str, str]) -> None:
        """ Print the BEL's enums and words as an instance parameter list """
        strs: List[str] = []

        # Dump enumerations in Verilog-compatible format
        for e in self.tiledata.cfg.cenums:
            bel, ename = e.name.split(".", 1)
            ename = ename.replace(".", "_")
            ename = param_renames.get(ename, ename)
            if bel == self.module_name:
                strs.append(f'  .{ename}("{e.value}")')
        # Dump initialization words in Verilog format
        for w in self.tiledata.cfg.cwords:
            bel, ename = w.name.split(".", 1)
            ename = ename.replace(".", "_")
            ename = param_renames.get(ename, ename)
            if bel == self.module_name:
                value = [str(int(c)) for c in w.value]
                valuestr = "".join(value[::-1])
                strs.append(f"  .{ename}({len(value)}'b{valuestr})")

        if strs:
            print(",\n".join(strs))

    def _print_pins(self) -> None:
        """ Print the BEL's enums and words as an instance parameter list """
        strs: List[str] = []

        # Dump input/output pins (already referenced to root pins), inputs first
        output_pins = set(self.pin_map.keys()) - set(self.input_pins)
        allpins = self.input_pins + natsorted(output_pins)
        defpin = "1'b0"
        for pin in allpins:
            strs.append(f"  .{pin}({self.pin_map.get(pin, defpin)})")

        if strs:
            print(",\n".join(strs))

    def print_instance(self, instname: str) -> None:
        """ Print the Verilog code for this specific module instance """
        raise NotImplementedError()


@dataclass
class SliceModule(Module):
    input_pins: ClassVar[List[str]] = [
        "A0",
        "B0",
        "C0",
        "D0",
        "A1",
        "B1",
        "C1",
        "D1",
        "M0",
        "M1",
        "FCI",
        "FXA",
        "FXB",
        "CLK",
        "LSR",
        "CE",
        "DI0",
        "DI1",
        "WD0",
        "WD1",
        "WAD0",
        "WAD1",
        "WAD2",
        "WAD3",
        "WRE",
        "WCK",
    ]

    output_pins: ClassVar[List[str]] = [
        "F0",
        "Q0",
        "F1",
        "Q1",
        "FCO",
        "OFX0",
        "OFX1",
        "WDO0",
        "WDO1",
        "WDO2",
        "WDO3",
        "WADO0",
        "WADO1",
        "WADO2",
        "WADO3",
    ]

    @classmethod
    def print_definition(cls) -> None:
        """ Print the Verilog code for the module definition """
        params = [
            "MODE",
            "GSR",
            "SRMODE",
            "CEMUX",
            "CLKMUX",
            "LSRMUX",
            "LUT0_INITVAL",
            "LUT1_INITVAL",
            "REG0_SD",
            "REG1_SD",
            "REG0_REGSET",
            "REG1_REGSET",
            "REG0_LSRMODE",
            "REG1_LSRMODE",
            "CCU2_INJECT1_0",
            "CCU2_INJECT1_1",
            "WREMUX",
            "WCKMUX",
            "A0MUX",
            "A1MUX",
            "B0MUX",
            "B1MUX",
            "C0MUX",
            "C1MUX",
            "D0MUX",
            "D1MUX",
        ]

        print(
            f"""
/* Use the cells_sim library from yosys/techlibs/ecp5 */
`include "../inc/cells_sim.v"
module ECP5_SLICE(
    input {", ".join(cls.input_pins)},
    output {", ".join(cls.output_pins)}
);

    /* These defaults correspond to all-zero-bit enumeration values */
    parameter MODE = "LOGIC";
    parameter GSR = "ENABLED";
    parameter SRMODE = "LSR_OVER_CE";
    parameter [127:0] CEMUX = "CE";
    parameter CLKMUX = "CLK";
    parameter LSRMUX = "LSR";
    parameter LUT0_INITVAL = 16'hFFFF;
    parameter LUT1_INITVAL = 16'hFFFF;
    parameter REG0_SD = "1";
    parameter REG1_SD = "1";
    parameter REG0_REGSET = "SET";
    parameter REG1_REGSET = "SET";
    parameter REG0_LSRMODE = "LSR";
    parameter REG1_LSRMODE = "LSR";
    parameter [127:0] CCU2_INJECT1_0 = "YES";
    parameter [127:0] CCU2_INJECT1_1 = "YES";
    parameter WREMUX = "WRE";
    parameter WCKMUX = "WCK";

    parameter A0MUX = "A0";
    parameter A1MUX = "A1";
    parameter B0MUX = "B0";
    parameter B1MUX = "B1";
    parameter C0MUX = "C0";
    parameter C1MUX = "C1";
    parameter D0MUX = "D0";
    parameter D1MUX = "D1";

    TRELLIS_SLICE #(
        {", ".join(f".{param}({param})" for param in params)}
    ) impl (
        {", ".join(f".{pin}({pin})" for pin in cls.input_pins)},
        {", ".join(f".{pin}({pin})" for pin in cls.output_pins)}
    );
endmodule
""".strip()
        )

    def print_instance(self, instname: str) -> None:
        print("ECP5_SLICE #(")
        self._print_parameters(
            {
                "K0_INIT": "LUT0_INITVAL",
                "K1_INIT": "LUT1_INITVAL",
            }
        )
        print(f") {instname} (")
        self._print_pins()
        print(");")
        print()


class EBRModule(Module):
    input_pins: ClassVar[List[str]] = [
        # Byte Enable wires
        "ADA0",
        "ADA1",
        "ADA2",
        "ADA3",
        # ADW
        "ADA5",
        "ADA6",
        "ADA7",
        "ADA8",
        "ADA9",
        "ADA10",
        "ADA11",
        "ADA12",
        "ADA13",
        # ADR
        "ADB5",
        "ADB6",
        "ADB7",
        "ADB8",
        "ADB9",
        "ADB10",
        "ADB11",
        "ADB12",
        "ADB13",
        "CEB",  # CER
        "CLKA",  # CLKW
        "CLKB",  # CLKR
        # DI
        "DIA0",
        "DIA1",
        "DIA2",
        "DIA3",
        "DIA4",
        "DIA5",
        "DIA6",
        "DIA7",
        "DIA8",
        "DIA9",
        "DIA10",
        "DIA11",
        "DIA12",
        "DIA13",
        "DIA14",
        "DIA15",
        "DIA16",
        "DIA17",
        "DIB0",
        "DIB1",
        "DIB2",
        "DIB3",
        "DIB4",
        "DIB5",
        "DIB6",
        "DIB7",
        "DIB8",
        "DIB9",
        "DIB10",
        "DIB11",
        "DIB12",
        "DIB13",
        "DIB14",
        "DIB15",
        "DIB16",
        "DIB17",
    ]

    output_pins: ClassVar[List[str]] = [
        # DO
        "DOA0",
        "DOA1",
        "DOA2",
        "DOA3",
        "DOA4",
        "DOA5",
        "DOA6",
        "DOA7",
        "DOA8",
        "DOA9",
        "DOA10",
        "DOA11",
        "DOA12",
        "DOA13",
        "DOA14",
        "DOA15",
        "DOA16",
        "DOA17",
        "DOB0",
        "DOB1",
        "DOB2",
        "DOB3",
        "DOB4",
        "DOB5",
        "DOB6",
        "DOB7",
        "DOB8",
        "DOB9",
        "DOB10",
        "DOB11",
        "DOB12",
        "DOB13",
        "DOB14",
        "DOB15",
        "DOB16",
        "DOB17",
    ]

    @classmethod
    def print_definition(cls) -> None:
        """ Print the Verilog code for the module definition """
        print(
            f"""
module ECP5_EBR(
    input {", ".join(cls.input_pins)},
    output {", ".join(cls.output_pins)}
);

    /* These defaults correspond to all-zero-bit enumeration values */
    parameter CSDECODE_A = 3'b111;
    parameter CSDECODE_B = 3'b111;
    parameter ADA0MUX = "ADA0";
    parameter ADA2MUX = "ADA2";
    parameter ADA3MUX = "ADA3";
    parameter ADB0MUX = "ADB0";
    parameter ADB1MUX = "ADB1";
    parameter CEAMUX = "CEA";
    parameter CEBMUX = "CEB";
    parameter CLKAMUX = "CLKA";
    parameter CLKBMUX = "CLKB";
    parameter DP16KD_DATA_WIDTH_A = "18";
    parameter DP16KD_DATA_WIDTH_B = "18";
    parameter DP16KD_WRITEMODE_A = "NORMAL";
    parameter DP16KD_WRITEMODE_B = "NORMAL";
    parameter MODE = "NONE";
    parameter OCEAMUX = "OCEA";
    parameter OCEBMUX = "OCEB";
    parameter PDPW16KD_DATA_WIDTH_R = "18";
    parameter PDPW16KD_RESETMODE = "SYNC";
    parameter WEAMUX = "WEA";
    parameter WEBMUX = "WEB";

    /* TODO! */

endmodule
""".strip()
        )

    def print_instance(self, instname: str) -> None:
        print("ECB5_EBR #(")
        self._print_parameters({})
        print(f") {instname} (")
        self._print_pins()
        print(");")
        print()


def print_verilog(graph: ConnectionGraph, tiles_by_loc: TilesByLoc) -> None:
    # Extract connected components and their roots & leaves
    sorted_components: List[Tuple[Component, List[Node], List[Node]]] = []
    for component in graph.get_components():
        roots = sorted([node for node in component.get_roots() if filter_node(node)])
        if not roots:
            continue
        leaves = sorted([node for node in component.get_leaves() if filter_node(node)])
        if not leaves:
            continue
        sorted_components.append((component, roots, leaves))
    sorted_components = sorted(sorted_components, key=lambda x: x[1][0])

    # Verilog input, output, and external wires
    mod_sources: Set[Node] = set()
    mod_sinks: Dict[Node, Node] = {}
    mod_globals: Set[Node] = set()

    def print_component(roots: Sequence[Node]) -> None:
        def visit(node: Node, level: int) -> None:
            print(" " * level, node, sep="")
            for x in graph.edges_fwd[node]:
                visit(x, level + 1)

        for root in roots:
            visit(root, 0)

    modules: Dict[str, Module] = {}

    print("/* Automatically generated by ecp_vlog.py")
    for component, roots, leaves in sorted_components:
        if len(roots) > 1:
            print()
            print("Unhandled multi-root component:")
            print(*roots, sep=", ")
            print(" -> ", end="")
            print(*leaves, sep=", ")
            continue

        mod_sources.add(roots[0])
        for node in leaves:
            mod_sinks[node] = roots[0]
        for node in roots + leaves:
            if node.mod_name in modules:
                modules[node.mod_name].pin_map[node.pin_name] = roots[0]
                continue

            mod_def = Module.create_from_node(node, tiles_by_loc)
            if not mod_def:
                mod_globals.add(node)
                continue
            mod_def.pin_map[node.pin_name] = roots[0]
            modules[node.mod_name] = mod_def

    # filter out any globals that are just copies of inputs or other outputs
    for node in mod_globals:
        if node in mod_sinks and mod_sinks[node] in mod_globals:
            print(f"filtered out useless output: {mod_sinks[node]} -> {node}")
            del mod_sinks[node]
    all_sources: Set[Node] = set()
    for sink in mod_sinks:
        all_sources.add(mod_sinks[sink])
    for node in mod_globals:
        if node in mod_sources and node not in all_sources:
            print(f"filtered out useless input: {node}")
            mod_sources.discard(node)
    print("*/")

    for mod_type in set(type(mod_def) for mod_def in modules.values()):
        mod_type.print_definition()

    print("module top(")
    mod_globals_vars = ["  input wire " + str(node) for node in mod_sources & mod_globals]
    mod_globals_vars += ["  output wire " + str(node) for node in set(mod_sinks) & mod_globals]
    print(",\n".join(natsorted(mod_globals_vars)))
    print(");")
    print()

    # sources are either connected to global inputs
    # or are outputs from some other node
    for node in natsorted(mod_sources - mod_globals, key=str):
        print(f"wire {node};")
    print()

    # sinks are either fed directly into a BEL,
    # in which case they are directly substituted,
    # or they are global outputs
    for node in natsorted(set(mod_sinks) & mod_globals, key=str):
        print(f"assign {node} = {mod_sinks[node]};")
    print()

    for modname in natsorted(modules):
        modules[modname].print_instance(modname)

    # debugging: print out any enums or words that we didn't handle in a Module
    print("/* Unhandled enums/words:")
    seen_enums: Set[Tuple[pytrellis.TileConfig, int]] = set()
    seen_words: Set[Tuple[pytrellis.TileConfig, int]] = set()
    for module in modules.values():
        for i, e in enumerate(module.tiledata.cfg.cenums):
            bel, _ = e.name.split(".", 1)
            if bel == module.module_name:
                seen_enums.add((module.tiledata.cfg, i))
        for i, w in enumerate(module.tiledata.cfg.cwords):
            bel, _ = w.name.split(".", 1)
            if bel == module.module_name:
                seen_words.add((module.tiledata.cfg, i))
    for loc in sorted(tiles_by_loc.keys(), key=lambda loc: (loc[1], loc[0])):
        for tiledata in tiles_by_loc[loc]:
            for i, e in enumerate(tiledata.cfg.cenums):
                if (tiledata.cfg, i) not in seen_enums:
                    print(" ", tiledata.tile.info.name, "enum:", e.name, e.value)
            for i, w in enumerate(tiledata.cfg.cwords):
                if (tiledata.cfg, i) not in seen_words:
                    valuestr = "".join([str(int(c)) for c in w.value][::-1])
                    print(" ", tiledata.tile.info.name, "word:", w.name, valuestr)
    print("*/")
    print("endmodule")


def main(argv: List[str]) -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser("Convert a .bit file into a .v verilog file for simulation")

    parser.add_argument("bitfile", help="Input .bit file")
    parser.add_argument("--package", help="Physical package (e.g. CABGA256), for renaming I/O-related wires")
    args = parser.parse_args(argv)

    pytrellis.load_database(database.get_db_root())

    bitstream = pytrellis.Bitstream.read_bit(args.bitfile)
    chip = bitstream.deserialise_chip()

    if args.package:
        dbfn = os.path.join(database.get_db_subdir(chip.info.family, chip.info.name), "iodb.json")
        with open(dbfn, "r") as f:
            iodb = json.load(f)

        # Rename PIO and IOLOGIC BELs based on their connected pins, for readability
        mod_renames = {}
        for pin_name, pin_data in iodb["packages"][args.package].items():
            mod_renames["R{row}C{col}_PIO{pio}".format(**pin_data)] = f"{pin_name}_PIO"
            mod_renames["R{row}C{col}_IOLOGIC{pio}".format(**pin_data)] = f"{pin_name}_IOLOGIC"

        Node.mod_name_map = mod_renames

    rgraph = chip.get_routing_graph()

    tiles_by_loc = make_tiles_by_loc(chip)
    graph = gen_config_graph(chip, rgraph, tiles_by_loc)
    print_verilog(graph, tiles_by_loc)


if __name__ == "__main__":
    main(sys.argv[1:])
