
configure_file(${CMAKE_SOURCE_DIR}/lib/common.h.in ${CMAKE_BINARY_DIR}/lib/common.h @ONLY IMMEDIATE)

# includes the standard Qt libraries
include(${QT_USE_FILE})

# includes our build files
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

set(FWBACKUPS_LIBRARY_SRC_FILES
    common.cpp
    config.cpp
    initialization.cpp
    logger.cpp
    )

add_library(fwbackups SHARED ${FWBACKUPS_LIBRARY_SRC_FILES})
set_target_properties(fwbackups PROPERTIES
    VERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}"
    SOVERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}"
    )
if(APPLE)
  set_target_properties(fwbackups PROPERTIES
      # Set the install_name on OS X
      INSTALL_NAME_DIR "@executable_path/../Resources"
      # Build with the same rpaths that will be used at install
      BUILD_WITH_INSTALL_RPATH ON
      )
endif(APPLE)

# link to Qt
target_link_libraries(fwbackups ${QT_LIBRARIES})


#include_directories(${fwbackups_SOURCE_DIR}/boxbackup/lib/win32
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/common
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/compress
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/crypto
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/server
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/backupclient
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/raidfile
#                    ${fwbackups_SOURCE_DIR}/boxbackup/lib/backupstore
#                   )
#link_directories("${fwbackups_SOURCE_DIR}/boxbackup")