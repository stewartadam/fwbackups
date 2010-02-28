
set(SERVER_SRC_FILES
    main.cpp
    server_admin.cpp
    configure_server.cpp
    manage_account.cpp
    )

set(SERVER_MOC_HDRS
    server_admin.h
    configure_server.h
    manage_account.h
    )

set(SERVER_UI_FILES
    ../../data/ui/server_admin/configure_server.ui
    ../../data/ui/server_admin/server_admin.ui
    ../../data/ui/server_admin/manage_account.ui
    )

set(RC_FILES ../../data/fwbackups.qrc)

qt4_add_resources(RC_SRCS ${RC_FILES}) # runs rcc
qt4_wrap_ui(SERVER_UI_HDRS ${SERVER_UI_FILES}) # runs uic
qt4_wrap_cpp(SERVER_MOC_SRCS ${SERVER_MOC_HDRS}) # runs moc

# includes the standard Qt libraries
include(${QT_USE_FILE})

# includes our build files and adds to linker search path
include_directories("${CMAKE_CURRENT_BINARY_DIR}")
include_directories("${fwbackups_SOURCE_DIR}/lib")
# This has to be included for common.h which we generate at configure time
include_directories("${fwbackups_BINARY_DIR}/lib")
link_directories("${fwbackups_BINARY_DIR}/lib")

# build the server executable
add_executable(fwbackups-serveradmin WIN32 MACOSX_BUNDLE ${SERVER_SRC_FILES} ${SERVER_MOC_SRCS} ${RC_SRCS} ${SERVER_UI_HDRS})

if(APPLE)
  # define some settings for the server admin app bundle
  set(MACOSX_BUNDLE_BUNDLE_NAME "fwbackups server administrator")
  set(MACOSX_BUNDLE_GUI_IDENTIFIER "com.diffingo.fwbackups-server-admin")
  set(MACOSX_BUNDLE_ICON_FILE "fwbackups.icns")
  set(MACOSX_BUNDLE_INFO_STRING "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}, Copyright 2005-2010 Stewart Adam")
  set(MACOSX_BUNDLE_SHORT_VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}")
  set(MACOSX_BUNDLE_LONG_VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")
  set(MACOSX_BUNDLE_BUNDLE_VERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")
  set(MACOSX_BUNDLE_COPYRIGHT "(C) 2005-2010 Stewart Adam")
  set_target_properties(fwbackups-serveradmin PROPERTIES
      OUTPUT_NAME "fwbackups server administrator"
      )
  
  # Allows for bundle re-creation just by running "make" and installs the icon file
  add_custom_target(osx_serveradmin_bundle_dirs
    COMMAND mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/fwbackups server administrator.app/Contents/Resources"
    COMMAND mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/fwbackups server administrator.app/Contents/MacOS"
    COMMAND cp "${CMAKE_SOURCE_DIR}/data/${MACOSX_BUNDLE_ICON_FILE}" "${CMAKE_CURRENT_BINARY_DIR}/fwbackups server administrator.app/Contents/Resources/${MACOSX_BUNDLE_ICON_FILE}"
    COMMAND cp "${fwbackups_BINARY_DIR}/lib/libfwbackups.${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}.dylib" "${CMAKE_CURRENT_BINARY_DIR}/fwbackups server administrator.app/Contents/Resources"
    #COMMAND cp *.qm "${CMAKE_CURRENT_BINARY_DIR}/fwbackups server administrator.app/Contents/Resources/"
    COMMENT "Configuring application bundle"
   )
  add_dependencies(fwbackups-serveradmin osx_serveradmin_bundle_dirs)
  add_dependencies(fwbackups-client fwbackups)
  # tell cmake where to place files inside the bundle
  set_source_files_properties(${fwbackups_RESOURCES} ${fwbackups_TRANSLATIONS} PROPERTIES MACOSX_PACKAGE_LOCATION Resources)
endif(APPLE)

# link against Qt and fwbackups
target_link_libraries(fwbackups-serveradmin ${QT_LIBRARIES})
target_link_libraries(fwbackups-serveradmin fwbackups)

