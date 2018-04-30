cmake_minimum_required(VERSION 3.10)
project(libtrellis)

set(CMAKE_CXX_STANDARD 14)

include_directories(include/)
add_library(trellis SHARED include/Bitstream.hpp src/Bitstream.cpp include/Chip.hpp include/CRAM.hpp src/CRAM.cpp)