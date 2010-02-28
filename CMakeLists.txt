project(fwbackups)
set(VERSION_MAJOR "1")
set(VERSION_MINOR "44")
set(VERSION_PATCH "0")

cmake_minimum_required(VERSION 2.6.0)

if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES "i386;x86_64")
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
