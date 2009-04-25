project(fwbackups)

set(VERSION_MAJOR "1")
set(VERSION_MINOR "44")
set(VERSION_PATCH "0")

cmake_minimum_required(VERSION 2.6.0)
if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES "ppc;i386")
endif(APPLE)

# we need gettext and qt4
find_package( Qt4 REQUIRED )
find_package( Gettext REQUIRED )

# enable warnings
add_definitions( -Wall )

# process subdirectories
add_subdirectory(po)
add_subdirectory(src)

# configure the pkgconfig file
configure_file( ${CMAKE_SOURCE_DIR}/fwbackups.pc.in
                ${CMAKE_BINARY_DIR}/fwbackups.pc @ONLY IMMEDIATE )

install(FILES "${CMAKE_BINARY_DIR}/fwbackups.pc" DESTINATION lib/pkgconfig)
