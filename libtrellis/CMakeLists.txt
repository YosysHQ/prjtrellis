cmake_minimum_required(VERSION 3.5)
project(libtrellis)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "-Wall -pedantic -Wextra -O3")
set(CMAKE_DEFIN)
set(boost_libs filesystem thread)
find_package(PythonInterp 3.5 REQUIRED)
find_package(PythonLibs 3.5 REQUIRED)

find_package(Boost REQUIRED COMPONENTS ${boost_libs})

set(version ${PYTHONLIBS_VERSION_STRING})

STRING( REGEX REPLACE "[^0-9]" "" boost_py_version ${version} )
find_package(Boost COMPONENTS "python-py${boost_py_version}" ${boost_libs})
set(Boost_PYTHON_FOUND ${Boost_PYTHON-PY${boost_py_version}_FOUND})

while(NOT "${version}" STREQUAL "" AND NOT Boost_PYTHON_FOUND)
    STRING( REGEX REPLACE "([0-9.]+).[0-9]+" "\\1" version ${version} )

    STRING( REGEX REPLACE "[^0-9]" "" boost_py_version ${version} )
    find_package(Boost COMPONENTS "python-py${boost_py_version}" ${boost_libs})
    set(Boost_PYTHON_FOUND ${Boost_PYTHON-PY${boost_py_version}_FOUND})

    STRING( REGEX MATCHALL "([0-9.]+).[0-9]+" has_more_version ${version} )
    if("${has_more_version}" STREQUAL "")
        break()
    endif()
endwhile()

if(NOT Boost_PYTHON_FOUND)
    find_package(Boost COMPONENTS python3 ${boost_libs})
endif()

include_directories(include/ ${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})

aux_source_directory(include/ INCLUDE_FILES)
aux_source_directory(src/ SOURCE_FILES)

add_library(trellis SHARED ${INCLUDE_FILES} ${SOURCE_FILES})
PYTHON_ADD_MODULE(pytrellis ${INCLUDE_FILES} ${SOURCE_FILES})
target_compile_definitions(pytrellis PRIVATE INCLUDE_PYTHON=1)
target_compile_definitions(trellis PRIVATE FUZZ_SAFETY_CHECK=1)
target_compile_definitions(pytrellis PRIVATE FUZZ_SAFETY_CHECK=1)
target_link_libraries(trellis LINK_PUBLIC ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
target_link_libraries(pytrellis LINK_PUBLIC ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
