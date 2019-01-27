cmake_minimum_required(VERSION 3.5)
project(libtrellis)

option(BUILD_PYTHON "Build Python Integration" ON)
option(BUILD_SHARED "Build shared Trellis library" ON)
option(STATIC_BUILD "Create static build of Trellis tools" OFF)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "-Wall -pedantic -Wextra -O3")
set(CMAKE_DEFIN)
set(link_param "")
if (STATIC_BUILD)
    set(Boost_USE_STATIC_LIBS   ON)
    if(NOT ${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
        set(link_param "-static")
    endif()
endif()
set(boost_libs filesystem thread)

find_package(PythonInterp 3.5 REQUIRED)

if (BUILD_PYTHON)
    find_package(PythonLibs 3.5 REQUIRED)
endif()

find_package(Boost REQUIRED COMPONENTS ${boost_libs})

if (BUILD_PYTHON)
    # Find Boost::Python of a suitable version in a cross-platform way
    # Some distributions (Arch) call it libboost_python3, others such as Ubuntu
    # call it libboost_python35. In the latter case we must consider all minor versions
    # Original source: https://github.com/BVLC/caffe/blob/master/cmake/Dependencies.cmake#L148
    set(version ${PYTHONLIBS_VERSION_STRING})

    STRING(REGEX REPLACE "[^0-9]" "" boost_py_version ${version})
    find_package(Boost COMPONENTS "python-py${boost_py_version}" ${boost_libs})
    set(Boost_PYTHON_FOUND ${Boost_PYTHON-PY${boost_py_version}_FOUND})

    while (NOT "${version}" STREQUAL "" AND NOT Boost_PYTHON_FOUND)
        STRING(REGEX REPLACE "([0-9.]+).[0-9]+" "\\1" version ${version})

        STRING(REGEX REPLACE "[^0-9]" "" boost_py_version ${version})
        find_package(Boost COMPONENTS "python-py${boost_py_version}" ${boost_libs})
        set(Boost_PYTHON_FOUND ${Boost_PYTHON-PY${boost_py_version}_FOUND})

        STRING(REGEX MATCHALL "([0-9.]+).[0-9]+" has_more_version ${version})
        if ("${has_more_version}" STREQUAL "")
            break()
        endif ()
    endwhile ()

    if (NOT Boost_PYTHON_FOUND)
        find_package(Boost COMPONENTS python3 ${boost_libs})
        if ("${Boost_LIBRARIES}" MATCHES ".*(python|PYTHON).*" )
            set(Boost_PYTHON_FOUND TRUE)
        endif ()
    endif ()

    if (NOT Boost_PYTHON_FOUND)
        find_package(Boost COMPONENTS python36 ${boost_libs})
        if ("${Boost_LIBRARIES}" MATCHES ".*(python|PYTHON).*" )
            set(Boost_PYTHON_FOUND TRUE)
        endif ()
    endif ()

    if (NOT Boost_PYTHON_FOUND)
        find_package(Boost COMPONENTS python37 ${boost_libs})
        if ("${Boost_LIBRARIES}" MATCHES ".*(python|PYTHON).*" )
            set(Boost_PYTHON_FOUND TRUE)
        endif ()
    endif ()

    if (NOT Boost_PYTHON_FOUND)
        STRING(REGEX REPLACE "([0-9]+\\.[0-9]+).*" "\\1" gentoo_version ${PYTHONLIBS_VERSION_STRING})
        find_package(Boost COMPONENTS python-${gentoo_version} ${boost_libs})
        if ("${Boost_LIBRARIES}" MATCHES ".*(python|PYTHON).*" )
            set(Boost_PYTHON_FOUND TRUE)
        endif ()
    endif ()

    if (NOT Boost_PYTHON_FOUND )
        message( FATAL_ERROR "No version of Boost::Python 3.x could be found.")
    endif ()
endif()

include_directories(include/ ${Boost_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIRS})

aux_source_directory(include/ INCLUDE_FILES)
aux_source_directory(src/ SOURCE_FILES)

if (BUILD_SHARED)
    add_library(trellis SHARED ${INCLUDE_FILES} ${SOURCE_FILES})
else()
    add_library(trellis STATIC ${INCLUDE_FILES} ${SOURCE_FILES})
endif()

target_link_libraries(trellis LINK_PUBLIC ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
if (BUILD_PYTHON)
    target_link_libraries(trellis LINK_PUBLIC ${PYTHON_LIBRARIES})
endif()

if (BUILD_PYTHON)
    PYTHON_ADD_MODULE(pytrellis ${INCLUDE_FILES} ${SOURCE_FILES})
    target_compile_definitions(pytrellis PRIVATE INCLUDE_PYTHON=1)
    target_link_libraries(pytrellis LINK_PUBLIC ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
endif()


find_package(Boost REQUIRED COMPONENTS program_options)

function(setup_rpath name)
  if(APPLE)
    set_target_properties(${name} PROPERTIES
                          BUILD_WITH_INSTALL_RPATH ON
                          INSTALL_RPATH "@loader_path/../lib"
                          INSTALL_NAME_DIR "@rpath")
  elseif(UNIX)
    set_target_properties(${name} PROPERTIES
                          BUILD_WITH_INSTALL_RPATH ON
                          INSTALL_RPATH "\$ORIGIN/../lib")
  endif()
endfunction()

add_executable(ecppack ${INCLUDE_FILES} tools/ecppack.cpp)
target_compile_definitions(ecppack PRIVATE TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecppack trellis ${Boost_LIBRARIES} ${link_param})
setup_rpath(ecppack)

add_executable(ecpunpack ${INCLUDE_FILES} tools/ecpunpack.cpp)
target_compile_definitions(ecpunpack PRIVATE TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecpunpack trellis ${Boost_LIBRARIES} ${link_param})
setup_rpath(ecpunpack)

add_executable(ecppll ${INCLUDE_FILES} tools/ecppll.cpp)
target_compile_definitions(ecppll PRIVATE TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecppll trellis ${Boost_LIBRARIES} ${link_param})
setup_rpath(ecppll)

if (BUILD_SHARED)
    install(TARGETS trellis ecppack ecppll ecpunpack LIBRARY DESTINATION lib  RUNTIME DESTINATION bin)
else()
    install(TARGETS ecppack ecpunpack ecppll RUNTIME DESTINATION bin)
endif()
install(DIRECTORY ../database DESTINATION share/trellis PATTERN ".git" EXCLUDE)
install(DIRECTORY ../misc DESTINATION share/trellis)
install(DIRECTORY ../util/common DESTINATION share/trellis/util)
install(DIRECTORY ../timing/util DESTINATION share/trellis/timing)
if (BUILD_SHARED)
   install(TARGETS pytrellis DESTINATION share/trellis/libtrellis)
endif()
