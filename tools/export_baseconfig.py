#!/usr/bin/env python3
import pytrellis
import sys
from os import path

def main(argv):
	print('#include "nextpnr.h"')
	print('#include "config.h"')
	print()
	print('NEXTPNR_NAMESPACE_BEGIN')
	print('namespace BaseConfigs {')
	for file in argv:
		name = path.splitext(path.basename(file))[0]
		name = name.replace('-', '_')
		with open(file, 'r') as f:
			cc = pytrellis.ChipConfig.from_string(f.read())
		print('void config_{}(ChipConfig &cc) {{'.format(name))
		print('    cc.chip_name = "{}";'.format(cc.chip_name))
		for meta in cc.metadata:
			print('    cc.metadata.push_back("{}");'.format(meta.replace("\n", "\\n")))
		for tile in cc.tiles:
			tn = tile.key()
			tc = tile.data()
			for arc in tc.carcs:
				print('    cc.tiles["{}"].add_arc("{}", "{}");'.format(tn, arc.sink, arc.source))
			for cw in tc.cwords:
				print('    cc.tiles["{}"].add_word("{}", std::vector<bool>{{{}}});'.format(tn, cw.name, ", ".join(["true" if x else "false" for x in cw.value])))
			for ce in tc.cenums:
				print('    cc.tiles["{}"].add_enum("{}", "{}");'.format(tn, ce.name, ce.value))
			for cu in tc.cunknowns:
				print('    cc.tiles["{}"].add_unknown({}, {});'.format(tn, cu.frame, cu.bit))
		print('}')
		print()
	print('}')
	print('NEXTPNR_NAMESPACE_END')

if __name__ == "__main__":
	main(sys.argv[1:])
