cmake_minimum_required(VERSION 3.5)
project(libtrellis)

option(BUILD_PYTHON "Build Python Integration" ON)
option(BUILD_SHARED "Build shared Trellis library" ON)
option(STATIC_BUILD "Create static build of Trellis tools" OFF)

set(CMAKE_CXX_STANDARD 14)
if (MSVC)
    set(CMAKE_CXX_FLAGS "-bigobj -EHsc")
else()
    set(CMAKE_CXX_FLAGS "-Wall -pedantic -Wextra -O3")
endif()
set(CMAKE_DEFIN)
set(link_param "")
if (STATIC_BUILD)
    set(Boost_USE_STATIC_LIBS ON)
    if (NOT APPLE)
        set(link_param "-static")
    endif()
else()
    if(MSVC)
        set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
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

    STRING(REGEX REPLACE "[^0-9]" "" boost_py_version "${version}")
    find_package(Boost COMPONENTS "python-py${boost_py_version}" ${boost_libs})
    set(Boost_PYTHON_FOUND ${Boost_PYTHON-PY${boost_py_version}_FOUND})

    while (NOT "${version}" STREQUAL "" AND NOT Boost_PYTHON_FOUND)
        STRING(REGEX REPLACE "([0-9.]+).[0-9]+" "\\1" version "${version}")

        STRING(REGEX REPLACE "[^0-9]" "" boost_py_version "${version}")
        find_package(Boost COMPONENTS "python-py${boost_py_version}" ${boost_libs})
        set(Boost_PYTHON_FOUND ${Boost_PYTHON-PY${boost_py_version}_FOUND})

        STRING(REGEX MATCHALL "([0-9.]+).[0-9]+" has_more_version "${version}")
        if ("${has_more_version}" STREQUAL "")
            break()
        endif ()
    endwhile ()

    if (NOT Boost_PYTHON_FOUND)
        foreach (PyVer 3 36 37 38)
            find_package(Boost COMPONENTS python${PyVer} ${boost_libs})
            if ("${Boost_LIBRARIES}" MATCHES ".*(python|PYTHON).*" )
                set(Boost_PYTHON_FOUND TRUE)
                break()
            endif ()
        endforeach ()
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

include(GNUInstallDirs)

file(RELATIVE_PATH TRELLIS_RPATH_LIBDIR /${CMAKE_INSTALL_BINDIR} /${CMAKE_INSTALL_LIBDIR})
file(RELATIVE_PATH TRELLIS_RPATH_DATADIR /${CMAKE_INSTALL_BINDIR} /${CMAKE_INSTALL_DATADIR})

function(setup_rpath name)
    if(APPLE)
        set_target_properties(${name} PROPERTIES
                              BUILD_WITH_INSTALL_RPATH ON
                              INSTALL_RPATH "@loader_path/${TRELLIS_RPATH_LIBDIR}/trellis"
                              INSTALL_NAME_DIR "@rpath")
    elseif(UNIX)
        set_target_properties(${name} PROPERTIES
                              BUILD_WITH_INSTALL_RPATH ON
                              INSTALL_RPATH "\$ORIGIN/${TRELLIS_RPATH_LIBDIR}/trellis")
    endif()
endfunction()


# Avoid perturbing build if git version hasn't changed
file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/generated")
set(LAST_GIT_VERSION "")
if (NOT DEFINED CURRENT_GIT_VERSION)
    execute_process(COMMAND git describe --tags OUTPUT_VARIABLE CURRENT_GIT_VERSION)
endif()
string(STRIP "${CURRENT_GIT_VERSION}" CURRENT_GIT_VERSION)
if (EXISTS "${CMAKE_BINARY_DIR}/generated/last_git_version")
    file(READ "${CMAKE_BINARY_DIR}/generated/last_git_version" LAST_GIT_VERSION)
endif()
if (NOT ("${LAST_GIT_VERSION}" STREQUAL "${CURRENT_GIT_VERSION}"))
    configure_file(
      ${CMAKE_SOURCE_DIR}/tools/version.cpp.in
      ${CMAKE_BINARY_DIR}/generated/version.cpp
    )
endif()
file(WRITE "${CMAKE_BINARY_DIR}/generated/last_git_version" CURRENT_GIT_VERSION)

add_executable(ecppack ${INCLUDE_FILES} tools/ecppack.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
target_include_directories(ecppack PRIVATE tools)
target_compile_definitions(ecppack PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecppack trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
setup_rpath(ecppack)

add_executable(ecpunpack ${INCLUDE_FILES} tools/ecpunpack.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
target_include_directories(ecpunpack PRIVATE tools)
target_compile_definitions(ecpunpack PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecpunpack trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
setup_rpath(ecpunpack)

add_executable(ecppll ${INCLUDE_FILES} tools/ecppll.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
target_include_directories(ecppll PRIVATE tools)
target_compile_definitions(ecppll PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecppll trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
setup_rpath(ecppll)

add_executable(ecpmulti ${INCLUDE_FILES} tools/ecpmulti.cpp "${CMAKE_BINARY_DIR}/generated/version.cpp")
target_include_directories(ecpmulti PRIVATE tools)
target_compile_definitions(ecpmulti PRIVATE TRELLIS_RPATH_DATADIR="${TRELLIS_RPATH_DATADIR}" TRELLIS_PREFIX="${CMAKE_INSTALL_PREFIX}")
target_link_libraries(ecpmulti trellis ${Boost_LIBRARIES} ${CMAKE_DL_LIBS} ${link_param})
setup_rpath(ecpmulti)

if (BUILD_SHARED)
    install(TARGETS trellis ecppack ecppll ecpunpack ecpmulti pytrellis
            LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/trellis
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
else()
    install(TARGETS ecppack ecpunpack ecppll ecpmulti
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
install(DIRECTORY ../database DESTINATION ${CMAKE_INSTALL_DATADIR}/trellis PATTERN ".git" EXCLUDE)
install(DIRECTORY ../misc DESTINATION ${CMAKE_INSTALL_DATADIR}/trellis)
install(DIRECTORY ../util/common DESTINATION ${CMAKE_INSTALL_DATADIR}/trellis/util)
install(DIRECTORY ../timing/util DESTINATION ${CMAKE_INSTALL_DATADIR}/trellis/timing USE_SOURCE_PERMISSIONS)
