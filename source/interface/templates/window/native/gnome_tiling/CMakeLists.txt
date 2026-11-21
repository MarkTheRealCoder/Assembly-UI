cmake_minimum_required(VERSION 3.16)
project(assembly-gnome-tiling LANGUAGES C CXX)

find_package(Qt5 5.15 REQUIRED COMPONENTS Gui)
if(NOT TARGET Qt5::GuiPrivate)
    message(FATAL_ERROR "Qt 5.15 private GUI headers are required (qtbase5-private-dev on Ubuntu)")
endif()
find_package(PkgConfig REQUIRED)
pkg_check_modules(WAYLAND REQUIRED IMPORTED_TARGET wayland-client)
find_program(WAYLAND_SCANNER wayland-scanner)
if(NOT WAYLAND_SCANNER)
    message(FATAL_ERROR "wayland-scanner is required to build the GNOME tiling monitor")
endif()

set(protocol "${CMAKE_CURRENT_SOURCE_DIR}/gtk-shell.xml")
set(protocol_header "${CMAKE_CURRENT_BINARY_DIR}/gtk-shell-client-protocol.h")
set(protocol_source "${CMAKE_CURRENT_BINARY_DIR}/gtk-shell-protocol.c")
add_custom_command(
    OUTPUT "${protocol_header}" "${protocol_source}"
    COMMAND "${WAYLAND_SCANNER}" client-header "${protocol}" "${protocol_header}"
    COMMAND "${WAYLAND_SCANNER}" private-code "${protocol}" "${protocol_source}"
    DEPENDS "${protocol}"
    VERBATIM
)

add_library(assembly-gnome-tiling MODULE gnome_tiling.cpp "${protocol_header}" "${protocol_source}")
target_compile_features(assembly-gnome-tiling PRIVATE cxx_std_11)
target_include_directories(assembly-gnome-tiling PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
target_link_libraries(assembly-gnome-tiling PRIVATE Qt5::GuiPrivate PkgConfig::WAYLAND)
