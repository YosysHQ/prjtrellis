cmake_minimum_required(VERSION 3.10)
project(libtrellis)

set(CMAKE_CXX_STANDARD 14)
find_package(PythonInterp)
find_package(PythonLibs)
find_package(Boost REQUIRED COMPONENTS python3 filesystem)
include_directories(include/ ${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})

aux_source_directory(include/ INCLUDE_FILES)
aux_source_directory(src/ SOURCE_FILES)

add_library(trellis SHARED ${INCLUDE_FILES} ${SOURCE_FILES})
PYTHON_ADD_MODULE(pytrellis ${INCLUDE_FILES} ${SOURCE_FILES})
target_link_libraries(trellis LINK_PUBLIC ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
target_link_libraries(pytrellis LINK_PUBLIC ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
