project('trellis', 'cpp',
         version : '1.0')

dep_boost_thread = dependency('boost', modules: 'thread')
dep_boost_python = dependency('boost', modules: 'python', required: false)

dep_boost_tools = dependency('boost', modules: ['filesystem', 'program_options'])

cc = meson.get_compiler('cpp')
dl_dep = cc.find_library('dl')

add_project_arguments('-DTRELLIS_RPATH_DATADIR="@0@"'.format(get_option('prefix')), language: 'cpp')

lib_src = [
  'libtrellis/src/Bels.cpp',
  'libtrellis/src/BitDatabase.cpp',
  'libtrellis/src/Bitstream.cpp',
  'libtrellis/src/ChipConfig.cpp',
  'libtrellis/src/Chip.cpp',
  'libtrellis/src/CRAM.cpp',
  'libtrellis/src/Database.cpp',
  'libtrellis/src/DedupChipdb.cpp',
  'libtrellis/src/PyTrellis.cpp',
  'libtrellis/src/RoutingGraph.cpp',
  'libtrellis/src/TileConfig.cpp',
  'libtrellis/src/Tile.cpp',
  'libtrellis/src/Util.cpp',
]

lib_inc = include_directories('libtrellis/include')

lib_trellis = library('trellis', lib_src,
                      include_directories: lib_inc,
                      dependencies: dep_boost_thread,
                      soversion: meson.project_version(),
                      install: true)

if dep_boost_python.found()
  library('pytrellis', lib_src,
          include_directories: lib_inc,
          dependencies: [dep_boost_thread, dep_boost_python],
          soversion: meson.project_version(),
          install: true)
else
  message('Boost::Python not found! Disabling python support...')
endif

version_inc = include_directories('libtrellis/tools')
version_src = vcs_tag(input: 'libtrellis/tools/version.cpp.in',
                      output: 'version.cpp',
                      replace_string: '@CURRENT_GIT_VERSION@')

executable('ecpbram', 'libtrellis/tools/ecpbram.cpp',
           include_directories: lib_inc,
           link_with: lib_trellis,
           dependencies: [dep_boost_tools, dl_dep],
           install: true)

executable('ecpmulti', ['libtrellis/tools/ecpmulti.cpp', version_src],
           include_directories: [lib_inc, version_inc],
           link_with: lib_trellis,
           dependencies: [dep_boost_tools, dl_dep],
           install: true)

executable('ecppack', ['libtrellis/tools/ecppack.cpp', version_src],
           include_directories: [lib_inc, version_inc],
           link_with: lib_trellis,
           dependencies: [dep_boost_tools, dl_dep],
           install: true)

executable('ecppll', ['libtrellis/tools/ecppll.cpp', version_src],
           include_directories: [lib_inc, version_inc],
           link_with: lib_trellis,
           dependencies: [dep_boost_tools, dl_dep],
           install: true)

executable('ecpunpack', ['libtrellis/tools/ecpunpack.cpp', version_src],
           include_directories: [lib_inc, version_inc],
           link_with: lib_trellis,
           dependencies: [dep_boost_tools, dl_dep],
           install: true)

data = [
  'misc/basecfgs/empty_lfe5u-25f.config',
  'misc/basecfgs/empty_lfe5u-25f.config',
  'misc/basecfgs/empty_lfe5u-25f.config',
  'misc/basecfgs/empty_lfe5um-25f.config',
  'misc/basecfgs/empty_lfe5um-25f.config',
  'misc/basecfgs/empty_lfe5um-85f.config',
  'misc/basecfgs/empty_lfe5um-85f.config',
  'misc/basecfgs/empty_lfe5um5g-45f.config',
  'misc/basecfgs/empty_lfe5um5g-45f.config',
  'misc/openocd/ecp5-evn.cfg',
  'misc/openocd/ecp5-versa.cfg',
  'misc/openocd/ecp5-versa5g.cfg',
  'misc/openocd/trellisboard.cfg',
  'misc/openocd/ulx3s.cfg',
  'misc/openocd/ulx3s.cfg',
  'util/common/database.py',
  'util/common/devices.py',
  'util/common/diamond.py',
  'util/common/isptcl.py',
  'util/common/nets.py',
  'util/common/tiles.py',
  'timing/util/cell_fuzzers.py',
  'timing/util/cell_html.py',
  'timing/util/cell_timings.py',
  'timing/util/design_pip_classes.py',
  'timing/util/extract_ncl_routing.py',
  'timing/util/interconnect_html.py',
  'timing/util/parse_sdf.py',
  'timing/util/pip_classes.py',
  'timing/util/timing_dbs.py',
  'timing/util/timing_solver.py',
]

install_data(data, rename: data, install_dir: 'share/trellis')

meson.add_install_script('install-db.sh')
