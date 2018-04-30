cmake_minimum_required(VERSION 3.10)
project(libtrellis)

set(CMAKE_CXX_STANDARD 14)

add_library(trellis SHARED include/Bitstream.hpp src/Bitstream.cpp)