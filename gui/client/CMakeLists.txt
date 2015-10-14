
set(CLIENT_SRC_FILES
    main.cpp
    fwbackups.cpp
    configure_backup.cpp
    restore.cpp
    ../custom_widgets.cpp
    )

set(CLIENT_MOC_HDRS
    fwbackups.h
    configure_backup.h
    restore.h
    ../custom_widgets.h
    )

set(CLIENT_UI_FILES
    ../../data/ui/client/fwbackups.ui
    ../../data/ui/client/choose_programs.ui
    ../../data/ui/client/configure_backup.ui
    ../../data/ui/client/export_sets.ui
    ../../data/ui/client/server_connections.ui
    ../../data/ui/client/prefs.ui
    ../../data/ui/client/restore.ui
    )

set(RC_FILES ../../data/fwbackups.qrc)

qt4_add_resources(RC_SRCS ${RC_FILES}) # runs rcc
qt4_wrap_ui(CLIENT_UI_HDRS ${CLIENT_UI_FILES}) # runs uic
qt4_wrap_cpp(CLIENT_MOC_SRCS ${CLIENT_MOC_HDRS}) # runs moc

# includes the standard Qt libraries
include(${QT_USE_FILE})

# includes our build files and adds to linker search path
include_directories("${CMAKE_CURRENT_BINARY_DIR}")
include_directories("${fwbackups_SOURCE_DIR}/gui")
include_directories("${fwbackups_SOURCE_DIR}/lib")
# This has to be included for common.h which we generate at configure time
include_directories("${fwbackups_BINARY_DIR}/lib")
link_directories("${fwbackups_BINARY_DIR}/lib")
link_directories("${fwbackups_BINARY_DIR}/lib")


# build the client executable
add_executable(fwbackups-client WIN32 MACOSX_BUNDLE ${CLIENT_SRC_FILES} ${CLIENT_MOC_SRCS} ${RC_SRCS} ${CLIENT_UI_HDRS})

if(APPLE)
  # define some settings for the client app bundle
  set(MACOSX_BUNDLE_BUNDLE_NAME "fwbackups")
  set(MACOSX_BUNDLE_GUI_IDENTIFIER "com.diffingo.fwbackups")
  set(MACOSX_BUNDLE_ICON_FILE "fwbackups.icns")
  set(MACOSX_BUNDLE_INFO_STRING "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}, Copyright 2005-2010 Stewart Adam")
  set(MACOSX_BUNDLE_SHORT_VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}")
  set(MACOSX_BUNDLE_LONG_VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")
  set(MACOSX_BUNDLE_BUNDLE_VERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")
  set(MACOSX_BUNDLE_COPYRIGHT "(C) 2005-2010 Stewart Adam")
  set_target_properties(fwbackups-client PROPERTIES
      OUTPUT_NAME "fwbackups"
      MACOSX_BUNDLE_INFO_PLIST ${CMAKE_SOURCE_DIR}/data/MacOSXBundleInfo.plist.in
      )

  # Allows for bundle re-creation just by running "make" and installs the icon file
  add_custom_target(osx_client_bundle_dirs
    COMMAND mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources"
    COMMAND mkdir -p "${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/MacOS"
    # current directory here is build/$platform/gui/client
    COMMAND cp "${CMAKE_SOURCE_DIR}/data/${MACOSX_BUNDLE_ICON_FILE}" "${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources/${MACOSX_BUNDLE_ICON_FILE}"
    COMMAND cp "${fwbackups_BINARY_DIR}/lib/libfwbackups.${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}.dylib" "${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources"
    #COMMAND cp *.qm "${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources/"
    COMMENT "Configuring application bundle"
   )
  add_dependencies(fwbackups-client osx_client_bundle_dirs)
  add_dependencies(fwbackups-client fwbackups-client)
  # tell cmake where to place files inside the bundle
  set_source_files_properties(${fwbackups_RESOURCES} ${fwbackups_TRANSLATIONS} PROPERTIES MACOSX_PACKAGE_LOCATION Resources)
endif(APPLE)

# link to Qt and fwbackups
target_link_libraries(fwbackups-client ${QT_LIBRARIES})
target_link_libraries(fwbackups-client fwbackups)
