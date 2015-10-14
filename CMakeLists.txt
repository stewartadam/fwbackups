project(fwbackups)

# FIXME: Check if running from a subdirectory of the source too
MACRO(FORCE_OUT_OF_SOURCE_BUILD)
  STRING(COMPARE EQUAL "${CMAKE_SOURCE_DIR}" "${CMAKE_BINARY_DIR}" insource)
  IF(insource)
    MESSAGE(FATAL_ERROR "${PROJECT_NAME} requires an out of source build.")
  ENDIF(insource)
ENDMACRO(FORCE_OUT_OF_SOURCE_BUILD)

FORCE_OUT_OF_SOURCE_BUILD()

set(VERSION_MAJOR "1")
set(VERSION_MINOR "44")
set(VERSION_PATCH "0")

cmake_minimum_required(VERSION 2.6.0)

if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES "x86_64")
endif(APPLE)

# Find required packages to build from source
find_package( Qt4 REQUIRED )
find_package( Gettext REQUIRED )

# Enable all compilation warnings
add_definitions( -Wall )

# Process subdirectories
add_subdirectory(lib)
add_subdirectory(gui)

# Create a pkgconfig file
configure_file(${CMAKE_SOURCE_DIR}/fwbackups.pc.in ${CMAKE_BINARY_DIR}/fwbackups.pc @ONLY IMMEDIATE)
