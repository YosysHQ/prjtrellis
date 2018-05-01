cmake_minimum_required(VERSION 3.10)
project(libtrellis)

set(CMAKE_CXX_STANDARD 14)
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(include/)
add_library(trellis SHARED include/Bitstream.hpp src/Bitstream.cpp include/Chip.hpp include/CRAM.hpp src/CRAM.cpp include/Util.hpp src/Util.cpp include/Database.hpp include/Tile.hpp src/Tile.cpp src/Database.cpp)
target_link_libraries(trellis LINK_PUBLIC ${Boost_LIBRARIES})