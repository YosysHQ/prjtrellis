cmake_minimum_required(VERSION 3.5)
project(libtrellis)

option(BUILD_PYTHON "Build Python Integration" ON)
option(BUILD_SHARED "Build shared Trellis library" ON)
option(STATIC_BUILD "Create static build of Trellis tools" OFF)
option(BUILD_ECPBRAM "Build the ecpbram tool" ON)
option(BUILD_ECPPACK "Build the ecppack tool" ON)
option(BUILD_ECPUNPACK "Build the ecppunpack tool" ON)
option(BUILD_ECPPLL "Build the ecppll tool" ON)
option(BUILD_ECPMULTI "Build the ecpmulti tool" ON)

set(PROGRAM_PREFIX "" CACHE STRING "Name prefix for executables")

set(CMAKE_CXX_STANDARD 14)
if (MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -bigobj -EHsc")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic -Wextra -O3")
endif()

set(link_param "")
if (STATIC_BUILD)
    set(Boost_USE_STATIC_LIBS ON)
    if(MSVC)
        add_definitions(-DBOOST_PYTHON_STATIC_LIB)
        set(CMAKE_CXX_FLAGS_RELEASE "/MT")
        set(CMAKE_CXX_FLAGS_DEBUG "/MTd")
    elseif (NOT APPLE)
        set(link_param "-static")
    endif()
else()
    if(MSVC)
        set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
    endif()
endif()

find_package(Threads)

if (WASI)
    add_definitions(
        -DBOOST_EXCEPTION_DISABLE
        -DBOOST_NO_EXCEPTIONS)
    if (NOT Threads_FOUND)
        add_definitions(-DBOOST_NO_CXX11_HDR_MUTEX)
    endif()
endif()

set(boost_libs filesystem program_options system)
if (Threads_FOUND)
    list(APPEND boost_libs thread)
else()
    add_definitions(-DNO_THREADS)
endif()
set(Boost_NO_BOOST_CMAKE ON)

find_package(Python3 3.5 REQUIRED COMPONENTS Interpreter)
if (BUILD_PYTHON)
    find_package(Python3 3.5 REQUIRED COMPONENTS Development)
    set(PythonInstallTarget "pytrellis")
endif()

find_package(Boost REQUIRED COMPONENTS ${boost_libs})

find_package(Git)

if (NOT DEFINED PYBIND11_INCLUDE_DIR)
    # Use bundled pybind11
    set(PYBIND11_INCLUDE_DIR "3rdparty/pybind11/include")
endif()

include_directories(include/ ${Boost_INCLUDE_DIRS} ${Python3_INCLUDE_DIRS} ${PYBIND11_INCLUDE_DIR})

aux_source_directory(include/ INCLUDE_FILES)
aux_source_directory(src/ SOURCE_FILES)

if (BUILD_SHARED)
    add_library(trellis SHARED ${INCLUDE_FILES} ${SOURCE_FILES})
else()
    add_library(trellis STATIC ${INCLUDE_FILES} ${SOURCE_FILES})
endif()

target_link_libraries(trellis LINK_PUBLIC ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
if (BUILD_PYTHON)
    target_link_libraries(trellis LINK_PUBLIC ${Python3_LIBRARIES})
endif()

if (BUILD_PYTHON)
    Python3_add_library(pytrellis MODULE ${INCLUDE_FILES} ${SOURCE_FILES})
    target_compile_definitions(pytrellis PRIVATE INCLUDE_PYTHON=1)
    if (APPLE)
        target_link_libraries(pytrellis LINK_PUBLIC ${Boost_LIBRARIES} ${Python3_LIBRARIES} "-undefined dynamic_lookup -bundle")
    else()
        target_link_libraries(pytrellis LINK_PUBLIC ${Boost_LIBRARIES} ${Python3_LIBRARIES})
    endif()
endif()

include(GNUInstallDirs)

file(RELATIVE_PATH TRELLIS_RPATH_LIBDIR /${CMAKE_INSTALL_BINDIR} /${CMAKE_INSTALL_LIBDIR})
file(RELATIVE_PATH TRELLIS_RPATH_DATADIR /${CMAKE_INSTALL_BINDIR} /${CMAKE_INSTALL_DATADIR})

function(setup_rpath name)
    if(APPLE)
        set_target_properties(${name} PROPERTIES
                              BUILD_WITH_INSTALL_RPATH ON
                              INSTALL_RPATH "@loader_path/${TRELLIS_RPATH_LIBDIR}/${PROGRAM_PREFIX}trellis"
                              INSTALL_NAME_DIR "@rpath")
    elseif(UNIX)
        set_target_properties(${name} PROPERTIES
                              BUILD_WITH_INSTALL_RPATH ON
                              INSTALL_RPATH "\$ORIGIN/${TRELLIS_RPATH_LIBDIR}/${PROGRAM_PREFIX}trellis")
    endif()
endfunction()


# Avoid perturbing build if git version hasn't changed
file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/generated")
set(LAST_GIT_VERSION "")
if (NOT DEFINED CURRENT_GIT_VERSION)
    execute_process(COMMAND git describe --tags --always OUTPUT_VARIABLE CURRENT_GIT_VERSION WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endif()
string(STRIP "${CURRENT_GIT_VERSION}" CURRENT_GIT_VERSION)
if (EXISTS "${CMAKE_BINARY_DIR}/generated/last_git_version")
    file(READ "${CMAKE_BINARY_DIR}/generated/last_git_version" LAST_GIT_VERSION)
endif()
if (NOT ("${LAST_GIT_VERSION}" STREQUAL "${CURRENT_GIT_VERSION}") OR NOT GIT_EXECUTABLE)
    configure_file(
      ${CMAKE_SOURCE_DIR}/tools/version.cpp.in
      ${CMAKE_BINARY_DIR}/generated/version.cpp
    )
endif()
file(WRITE "${CMAKE_BINARY_DIR}/generated/last_git_version" CURRENT_GIT_VERSION)

if (BUILD_ECPBRAM)
    add_executable(${PROGRAM_PREFIX}ecpbram ${INCLUDE_FILES} tools/ecpbram.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
    target_include_directories(${PROGRAM_PREFIX}ecpbram PRIVATE tools)
    target_compile_definitions(${PROGRAM_PREFIX}ecpbram PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}" TRELLIS_PROGRAM_PREFIX="${PROGRAM_PREFIX}")
    target_link_libraries(${PROGRAM_PREFIX}ecpbram trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
    setup_rpath(${PROGRAM_PREFIX}ecpbram)
    if (WASI)
        set_property(TARGET ${PROGRAM_PREFIX}ecpbram PROPERTY SUFFIX ".wasm")
    endif()
    install(TARGETS ${PROGRAM_PREFIX}ecpbram RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

if (BUILD_ECPPACK)
    add_executable(${PROGRAM_PREFIX}ecppack ${INCLUDE_FILES} tools/ecppack.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
    target_include_directories(${PROGRAM_PREFIX}ecppack PRIVATE tools)
    target_compile_definitions(${PROGRAM_PREFIX}ecppack PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}" TRELLIS_PROGRAM_PREFIX="${PROGRAM_PREFIX}")
    target_link_libraries(${PROGRAM_PREFIX}ecppack trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
    setup_rpath(${PROGRAM_PREFIX}ecppack)
    if (WASI)
        set_property(TARGET ${PROGRAM_PREFIX}ecppack PROPERTY SUFFIX ".wasm")
    endif()
    install(TARGETS ${PROGRAM_PREFIX}ecppack RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

if (BUILD_ECPUNPACK)
    add_executable(${PROGRAM_PREFIX}ecpunpack ${INCLUDE_FILES} tools/ecpunpack.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
    target_include_directories(${PROGRAM_PREFIX}ecpunpack PRIVATE tools)
    target_compile_definitions(${PROGRAM_PREFIX}ecpunpack PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}" TRELLIS_PROGRAM_PREFIX="${PROGRAM_PREFIX}")
    target_link_libraries(${PROGRAM_PREFIX}ecpunpack trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
    setup_rpath(${PROGRAM_PREFIX}ecpunpack)
    if (WASI)
        set_property(TARGET ${PROGRAM_PREFIX}ecpunpack PROPERTY SUFFIX ".wasm")
    endif()
    install(TARGETS ${PROGRAM_PREFIX}ecpunpack RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

if (BUILD_ECPPLL)
    add_executable(${PROGRAM_PREFIX}ecppll ${INCLUDE_FILES} tools/ecppll.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
    target_include_directories(${PROGRAM_PREFIX}ecppll PRIVATE tools)
    target_compile_definitions(${PROGRAM_PREFIX}ecppll PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}" TRELLIS_PROGRAM_PREFIX="${PROGRAM_PREFIX}")
    target_link_libraries(${PROGRAM_PREFIX}ecppll trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
    setup_rpath(${PROGRAM_PREFIX}ecppll)
    if (WASI)
        set_property(TARGET ${PROGRAM_PREFIX}ecppll PROPERTY SUFFIX ".wasm")
    endif()
    install(TARGETS ${PROGRAM_PREFIX}ecppll RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

if (BUILD_ECPMULTI)
    add_executable(${PROGRAM_PREFIX}ecpmulti ${INCLUDE_FILES} tools/ecpmulti.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
    target_include_directories(${PROGRAM_PREFIX}ecpmulti PRIVATE tools)
    target_compile_definitions(${PROGRAM_PREFIX}ecpmulti PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}" TRELLIS_PROGRAM_PREFIX="${PROGRAM_PREFIX}")
    target_link_libraries(${PROGRAM_PREFIX}ecpmulti trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
    setup_rpath(${PROGRAM_PREFIX}ecpmulti)
    if (WASI)
        set_property(TARGET ${PROGRAM_PREFIX}ecpmulti PROPERTY SUFFIX ".wasm")
    endif()
    install(TARGETS ${PROGRAM_PREFIX}ecpmulti RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()


if (BUILD_SHARED)
    install(TARGETS trellis ${PythonInstallTarget} LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/${PROGRAM_PREFIX}trellis)
endif()

install(DIRECTORY ../database DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROGRAM_PREFIX}trellis PATTERN ".git" EXCLUDE)
install(DIRECTORY ../misc DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROGRAM_PREFIX}trellis)
install(DIRECTORY ../util/common DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROGRAM_PREFIX}trellis/util)
install(DIRECTORY ../timing/util DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROGRAM_PREFIX}trellis/timing)
install(PROGRAMS ../timing/util/cell_html.py DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROGRAM_PREFIX}trellis/timing/util)
install(PROGRAMS ../timing/util/cell_timings.py DESTINATION ${CMAKE_INSTALL_DATADIR}/${PROGRAM_PREFIX}trellis/timing/util)
