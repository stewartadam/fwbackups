set(SRC_FILES
    common.cpp
    config.cpp
    initialization.cpp
    logger.cpp
    main.cpp
    interface/qt4/fwbackups.cpp
    interface/qt4/configBackup.cpp
    interface/qt4/restore.cpp
    interface/qt4/custom_widgets.cpp
   )

set(MOC_HDRS
    interface/qt4/fwbackups.h
    interface/qt4/configBackup.h
    interface/qt4/restore.h
    interface/qt4/custom_widgets.h
    )

set(UI_FILES
    ../data/ui/fwbackups.ui
    ../data/ui/choosePrograms.ui
    ../data/ui/configBackup.ui
    ../data/ui/exportSets.ui
    ../data/ui/manageKeys.ui
    ../data/ui/prefs.ui
    ../data/ui/restore.ui
    )

set(RC_FILES ../data/fwbackups.qrc)

qt4_add_resources( RC_SRCS ${RC_FILES} ) # runs rcc
qt4_wrap_ui( UI_HDRS ${UI_FILES} ) # runs uic
qt4_wrap_cpp( MOC_SRCS ${MOC_HDRS} ) # runs moc

# includes the standard Qt libraries
include( ${QT_USE_FILE} )

include_directories( ${fwbackups_BINARY_DIR}/src )
include_directories( ${fwbackups_SOURCE_DIR}/src )


if( APPLE )
  # define some settings for the Bundle
  set( MACOSX_BUNDLE_BUNDLE_NAME fwbackups )
  set( MACOSX_BUNDLE_GUI_IDENTIFIER "fwbackups" )
  set( MACOSX_BUNDLE_ICON_FILE fwbackups.icns )
  set( MACOSX_BUNDLE_INFO_STRING ""${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}", Copyright 2005-2009 fwbackups team" )
  set( MACOSX_BUNDLE_SHORT_VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}" )
  set( MACOSX_BUNDLE_LONG_VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}" )
  set( MACOSX_BUNDLE_BUNDLE_VERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}" )
  set( MACOSX_BUNDLE_COPYRIGHT "(C) 2005-2009 Stewart Adam" )
  
  # build the executable
  add_executable( fwbackups MACOSX_BUNDLE ${SRC_FILES} ${MOC_SRCS} ${RC_SRCS} ${UI_HDRS} )
  
  # Allows for bundle re-creation just by running "make" and installs icon
  add_custom_target( osx_bundle_dirs
    COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources
    COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/MacOS
    COMMAND cp ../../../data/${MACOSX_BUNDLE_ICON_FILE} ${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources/${MACOSX_BUNDLE_ICON_FILE}
    #COMMAND cp *.qm ${CMAKE_CURRENT_BINARY_DIR}/fwbackups.app/Contents/Resources/
   )
  add_dependencies( fwbackups osx_bundle_dirs )
  # tell cmake where to place files inside the bundle
  set_source_files_properties( ${fwbackups_RESOURCES} ${fwbackups_TRANSLATIONS} PROPERTIES MACOSX_PACKAGE_LOCATION Resources )
else( NOT APPLE )
  # Non-CLI binary for windows, regular for Linux
  add_executable( fwbackups WIN32 ${SRC_FILES} ${MOC_SRCS} ${RC_SRCS} ${UI_HDRS} )
endif( APPLE )

# link Qt to the executable
target_link_libraries( fwbackups ${QT_LIBRARIES} )

#if( UNIX AND NOT APPLE )
