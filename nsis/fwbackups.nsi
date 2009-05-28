; fwbackups.nsi
; The fwbackups installer file

;--------------------------------
;Notes
; Section /o --> NOT selected by default
; SectionGroup /e --> Expanded b default

;--------------------------------
;Includes
  !include "MUI.nsh"
  !include "sections.nsh"
  !include "WinVer.nsh"
  !include "LogicLib.nsh"

  !include "FileFunc.nsh"
  !insertmacro GetParameters
  !insertmacro GetOptions
  !insertmacro GetParent

  !include "WordFunc.nsh"
  !insertmacro VersionCompare

;--------------------------------
;Version resource
;Remember the installer name doesn't change when this does
  !define PRODUCT_NAME                    "fwbackups"
  !define PRODUCT_PREREL                 "rc2"
  !define PRODUCT_VERSION                 "1.43.3"
  !define PRODUCT_PUBLISHER               "Stewart Adam"
  !define PRODUCT_WEB_SITE                "http://www.diffingo.com/opensource"

  VIProductVersion                        "${PRODUCT_VERSION}.0"
  VIAddVersionKey "ProductName"           "${PRODUCT_NAME}"
  VIAddVersionKey "FileVersion"           "${PRODUCT_VERSION} ${PRODUCT_PREREL}"
  VIAddVersionKey "ProductVersion"        "${PRODUCT_VERSION}"
  VIAddVersionKey "LegalCopyright"        "(C) 2005 - 2009 Stewart Adam"
  VIAddVersionKey "FileDescription"       "fwbackups Installer (w/ Requirements)"

;--------------------------------
;General
;--------------------------------
;General
  Name                                    "fwbackups"
  OutFile                                 "fwbackups-1.43.3rc2-Setup.exe"
  InstallDir                              $PROGRAMFILES\fwbackups
  Var name
  Var GTK_FOLDER
  Var ISSILENT
  SetCompressor /SOLID lzma
  ShowInstDetails show
  ShowUninstDetails show
  !define PRODUCT_REG_KEY                 "SOFTWARE\fwbackups"
  !define PRODUCT_UNINSTALL_KEY           "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\fwbackups"

  !define HKLM_APP_PATHS_KEY              "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\fwbackups-runapp.pyw"
  !define STARTUP_RUN_KEY                 "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
  !define PRODUCT_UNINST_EXE              "fwbackups-uninst.exe"
  !define GTK_MIN_VERSION                 "2.6.10"
  !define GTK_INSTALL_VERSION             "2.14.7"
  !define GTK_REG_KEY                     "SOFTWARE\GTK\2.0"
  !define GTK_DEFAULT_INSTALL_PATH        "$COMMONFILES\GTK\2.0"
  !define GTK_RUNTIME_INSTALLER           "gtk-runtime-2.14.7-rev-a"
  !define PYTHON_RUNTIME_INSTALLER        "python-2.6.2.msi"
  !define PYGTK_MODULE_INSTALLER          "pygtk-2.12.1-3.win32-py2.6.exe"
  !define PYCAIRO_MODULE_INSTALLER        "pycairo-1.4.12-2.win32-py2.6.exe"
  !define PYGOBJECT_MODULE_INSTALLER      "pygobject-2.14.2-2.win32-py2.6.exe"
  !define PYCRON_INSTALLER                "pycron-0.5.9.0.exe"

;--------------------------------
; Interface settings:
  !define MUI_ICON "..\pixmaps\fwbackups.ico"
  !define MUI_UNICON "..\pixmaps\fwbackups_un.ico"
;  !define MUI_WELCOMEFINISHPAGE_BITMAP    ".\pixmaps\pidgin-intro.bmp"
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP          "..\pixmaps\fwbackups_nsis.bmp"
  !define MUI_HEADERIMAGE_UNBITMAP        "..\pixmaps\fwbackups_nsis.bmp"
  !define MUI_LANGDLL_REGISTRY_ROOT       "HKCU"
  !define MUI_LANGDLL_REGISTRY_KEY        ${PRODUCT_REG_KEY}
  !define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"
  !define MUI_COMPONENTSPAGE_SMALLDESC
  !define MUI_ABORTWARNING

  !define MUI_FINISHPAGE_NOAUTOCLOSE
  ;!define MUI_FINISHPAGE_RUN             "python $INSTDIR\fwbackups-runapp.pyw"
  ;!define MUI_FINISHPAGE_RUN_NOTCHECKED
  !define MUI_FINISHPAGE_LINK             $(lng_VisitTheWebsite)
  !define MUI_FINISHPAGE_LINK_LOCATION    "${PRODUCT_WEB_SITE}"

;  !define MUI_WELCOMEFINISHPAGE_BITMAP   ".\pixmaps\pidgin-intro.bmp"

;--------------------------------
;Pages
  !define MUI_PAGE_CUSTOMFUNCTION_PRE     preWelcomePage
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE           "copying.rtf"
  !insertmacro MUI_PAGE_COMPONENTS
  ; gtk installer
  !define MUI_PAGE_CUSTOMFUNCTION_PRE     preGtkDirPage
  !define MUI_PAGE_CUSTOMFUNCTION_LEAVE   postGtkDirPage
  ;!define MUI_DIRECTORYPAGE_VARIABLE     $GTK_FOLDER
  ;!insertmacro MUI_PAGE_DIRECTORY
  ; /gtk installer
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Language files
  !include "english.nsh"

;--------------------------------
;Installer Sections
  !define PYINSTDIR "$PYDIR\Lib\site-packages\fwbackups"
  ;InstType $(lng_Full)
  ;InstType $(lng_Minimal)

Section -SecUninstallOldfwbackups
  ; check for an old installation and clean it
  ClearErrors
  DetailPrint "Checking for old versions..."
  IfFileExists "$INSTDIR\fwbackups-uninst.exe" Present NotPresent
  Present:
    DetailPrint "Old version found!"
    MessageBox MB_YESNO $(lng_AlreadyInstalled) /SD IDYES IDNO NotPresent
    ClearErrors
    DetailPrint "Running uninstaller..."
    ExecWait '"$INSTDIR\fwbackups-uninst.exe" _?=$INSTDIR'
  NotPresent:
      DetailPrint "Starting installation..."
SectionEnd

;--------------------------------
;GTK+ Runtime Install Section
Section $(lng_GtkRuntime) SecGtk

  Call CheckUserInstallRights
  Pop $R1

  SetOutPath $TEMP
  SetOverwrite on
  File /oname=gtk-runtime.exe "..\..\..\..\installers\${GTK_RUNTIME_INSTALLER}"
  SetOverwrite off

  Call DoWeNeedGtk
  Pop $R0
  Pop $R6

  StrCmp $R0 "0" have_gtk
  StrCmp $R0 "1" upgrade_gtk
  StrCmp $R0 "2" upgrade_gtk

  ;no_gtk:
    StrCmp $R1 "NONE" gtk_no_install_rights

    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT /D=$GTK_FOLDER'

    IfErrors gtk_install_error done

  upgrade_gtk:
    StrCpy $GTK_FOLDER $R6
    ;!insertmacro install_win32
    StrCmp $R0 "2" +2 ; Upgrade isn't optional
    MessageBox MB_YESNO $(lng_PromptUpgradeGtk) /SD IDYES IDNO done
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE /S /D=$GTK_FOLDER'
    IfErrors gtk_install_error done

    gtk_install_error:
      Delete "$TEMP\gtk-runtime.exe"
      MessageBox MB_OK $(lng_GtkInstallError) /SD IDOK
      Quit

  have_gtk:
    StrCpy $GTK_FOLDER $R6
    ;!insertmacro install_win32 
    StrCmp $R1 "NONE" done ; If we have no rights, we can't re-install
    ; Even if we have a sufficient version of GTK+, we give user choice to re-install.
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT'
    IfErrors gtk_install_error
    Goto done

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end got_install rights

  gtk_no_install_rights:
    ; Install GTK+ to fwbackups install dir
    StrCpy $GTK_FOLDER $INSTDIR
    ;!insertmacro install_win32 
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT /D=$GTK_FOLDER'
    IfErrors gtk_install_error
      SetOverwrite on
      ClearErrors
      CopyFiles /FILESONLY "$GTK_FOLDER\bin\*.dll" $GTK_FOLDER
      SetOverwrite off
      IfErrors gtk_install_error
        Delete "$GTK_FOLDER\bin\*.dll"
        Goto done
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end gtk_no_install_rights

  done:
    Delete "$TEMP\gtk-runtime.exe"
SectionEnd ; end of GTK+ section

;--------------------------------
;Python Install Section
Section $(lng_Python) SecPython
  ;TODO: Check if already installed; Check upgrade.
  ;TODO: Set the proper Start Menu/Programs target
  ;TODO: Check if msiexec exists and point the user
  ;the Win98/ME, W2K MSI Installer webpage, the links
  ;are in http://www.python.org/download/releases/2.5/

  SetOutPath "$INSTDIR"
  File "..\..\..\..\installers\${PYTHON_RUNTIME_INSTALLER}"

  ;Installing
  ExecWait 'msiexec /i "$INSTDIR\${PYTHON_RUNTIME_INSTALLER}" TARGETDIR="$PROGRAMFILES\Python25" /qb!'
  delete "$INSTDIR\${PYTHON_RUNTIME_INSTALLER}"
SectionEnd

;--------------------------------
;Python Modules Install Section
SectionGroup /e $(lng_PyModules) SecPyModules
  Section $(lng_PyGTK) SecPyGTK
  SetOutPath "$INSTDIR"
  File "..\..\..\..\installers\${PYGTK_MODULE_INSTALLER}"
  ExecWait $INSTDIR\${PYGTK_MODULE_INSTALLER}
  delete $INSTDIR\${PYGTK_MODULE_INSTALLER}
  SectionEnd

  Section $(lng_PyCairo) SecPyCairo
  SetOutPath "$INSTDIR"
  File "..\..\..\..\installers\${PYCAIRO_MODULE_INSTALLER}"
  ExecWait $INSTDIR\${PYCAIRO_MODULE_INSTALLER}
  delete $INSTDIR\${PYCAIRO_MODULE_INSTALLER}
  SectionEnd

  Section $(lng_PyGObject) SecPyGObject
  SetOutPath "$INSTDIR"
  File "..\..\..\..\installers\${PYGOBJECT_MODULE_INSTALLER}"
  ExecWait $INSTDIR\${PYGOBJECT_MODULE_INSTALLER}
  delete $INSTDIR\${PYGOBJECT_MODULE_INSTALLER}
  SectionEnd
SectionGroupEnd

;--------------------------------
;PyCron Install Section
Section $(lng_PyCron) SecPyCron
  SetOutPath "$INSTDIR"
  File "..\..\..\..\installers\${PYCRON_INSTALLER}"
  ExecWait $INSTDIR\${PYCRON_INSTALLER}
  delete $INSTDIR\${PYCRON_INSTALLER}
SectionEnd

;--------------------------------
;fwbackups Install Section
Section $(lng_fwbackupsPackage) Secfwbackups
  SectionIn 1 RO

  ; Check install rights..
  Call CheckUserInstallRights
  Pop $R0

  ; Get GTK+ lib dir if we have it..

  StrCmp $R0 "NONE" fwbackups_none
  StrCmp $R0 "HKLM" fwbackups_hklm fwbackups_hkcu

  fwbackups_hklm:
    ReadRegStr $R1 HKLM ${GTK_REG_KEY} "Path"
    WriteRegStr HKLM "${HKLM_APP_PATHS_KEY}" "" "$INSTDIR\fwbackups-runapp.pyw"
    WriteRegStr HKLM "${HKLM_APP_PATHS_KEY}" "Path" "$R1\bin"
    WriteRegStr HKLM ${PRODUCT_REG_KEY} "" "$INSTDIR"
    WriteRegStr HKLM ${PRODUCT_REG_KEY} "Version" "${PRODUCT_VERSION}"
    WriteRegStr HKLM "${PRODUCT_UNINSTALL_KEY}" "DisplayName" "fwbackups"
    WriteRegStr HKLM "${PRODUCT_UNINSTALL_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKLM "${PRODUCT_UNINSTALL_KEY}" "HelpLink" "http://www.diffingo.com/opensource"
    WriteRegDWORD HKLM "${PRODUCT_UNINSTALL_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${PRODUCT_UNINSTALL_KEY}" "NoRepair" 1
    WriteRegStr HKLM "${PRODUCT_UNINSTALL_KEY}" "UninstallString" "$INSTDIR\${PRODUCT_UNINST_EXE}"
    ; Sets scope of the desktop and Start Menu entries for all users.
    SetShellVarContext "all"
    Goto fwbackups_install_files

  fwbackups_hkcu:
    ReadRegStr $R1 HKCU ${GTK_REG_KEY} "Path"
    StrCmp $R1 "" 0 +2
      ReadRegStr $R1 HKLM ${GTK_REG_KEY} "Path"

    WriteRegStr HKCU ${PRODUCT_REG_KEY} "" "$INSTDIR"
    WriteRegStr HKCU ${PRODUCT_REG_KEY} "Version" "${PRODUCT_VERSION}"
    WriteRegStr HKCU "${PRODUCT_UNINSTALL_KEY}" "DisplayName" "fwbackups"
    WriteRegStr HKCU "${PRODUCT_UNINSTALL_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKCU "${PRODUCT_UNINSTALL_KEY}" "HelpLink" "http://www.diffingo.com/opensource"
    WriteRegDWORD HKCU "${PRODUCT_UNINSTALL_KEY}" "NoModify" 1
    WriteRegDWORD HKCU "${PRODUCT_UNINSTALL_KEY}" "NoRepair" 1
    WriteRegStr HKCU "${PRODUCT_UNINSTALL_KEY}" "UninstallString" "$INSTDIR\${PRODUCT_UNINST_EXE}"
    Goto fwbackups_install_files

  fwbackups_none:
    ReadRegStr $R1 HKLM ${GTK_REG_KEY} "Path"

  fwbackups_install_files:
    SetOutPath "$INSTDIR"
    ; fwbackups files
    SetOverwrite on
    File ..\..\..\..\installers\libglade-2.0-0.dll
    File ..\..\..\..\installers\libxml2.dll
    File ..\AUTHORS
    File ..\CHANGELOG
    File ..\COPYING
    File ..\README
    File ..\TODO
    File ..\src\BugReport.glade
    File ..\src\fwbackups.glade
    File ..\src\fwbackups-runapp.pyw
    File ..\src\cronwriter.py
    File ..\pixmaps\fwbackups.ico
    File ..\bin\fwbackups-run.py
    File ..\bin\fwbackups-runonce.py
    SetOutPath "$INSTDIR\fwbackups"
    File /r ..\src\fwbackups\*.py

    SetOutPath "$INSTDIR"

    ; If we don't have install rights we're done
    StrCmp $R0 "NONE" done
    SetOverwrite off

    ; write out uninstaller
    SetOverwrite on
    WriteUninstaller "$INSTDIR\${PRODUCT_UNINST_EXE}"
    SetOverwrite off

  done:
SectionEnd ; end of default fwbackups section

;--------------------------------
;Shortcuts

SectionGroup /e $(lng_Shortcuts) SecShortcuts
  Section /o $(lng_Desktop) SecDesktopShortcut
    SetOverwrite on
    CreateShortCut "$DESKTOP\fwbackups.lnk" "$INSTDIR\fwbackups-runapp.pyw" "" "$INSTDIR\fwbackups.ico" 0
    SetOverwrite off
  SectionEnd
  Section $(lng_StartMenu) SecStartMenuShortcut
    SetOverwrite on
    SetShellVarContext all
    CreateShortCut "$SMPROGRAMS\fwbackups.lnk" "$INSTDIR\fwbackups-runapp.pyw" "" "$INSTDIR\fwbackups.ico" 0
    SetShellVarContext current
    SetOverwrite off
  SectionEnd  
SectionGroupEnd

;--------------------------------
;Uninstaller Section

Section Uninstall
  Call un.CheckUserInstallRights
  Pop $R0
  StrCmp $R0 "NONE" no_rights
  StrCmp $R0 "HKCU" try_hkcu try_hklm
  Delete $INSTDIR\AUTHORS
  Delete $INSTDIR\CHANGELOG
  Delete $INSTDIR\COPYING
  Delete $INSTDIR\README
  Delete $INSTDIR\TODO
  Delete $INSTDIR\BugReport.glade
  Delete $INSTDIR\fwbackups.glade
  Delete $INSTDIR\fwbackups-runapp.pyw
  Delete $INSTDIR\cronwriter.py
  Delete $INSTDIR\fwbackups.ico
  Delete $INSTDIR\fwbackups-run.py
  Delete $INSTDIR\fwbackups-runonce.py
  RMDir /r $INSTDIR\fwbackups
  RMDir /r $INSTDIR\win32
  try_hkcu:
    ReadRegStr $R0 HKCU ${PRODUCT_REG_KEY} ""
    StrCmp $R0 $INSTDIR 0 cant_uninstall
      ; HKCU install path matches our INSTDIR so uninstall
      DeleteRegKey HKCU ${PRODUCT_REG_KEY}
      DeleteRegKey HKCU "${PRODUCT_UNINSTALL_KEY}"
      Goto cont_uninstall

  try_hklm:
    ReadRegStr $R0 HKLM ${PRODUCT_REG_KEY} ""
    StrCmp $R0 $INSTDIR 0 try_hkcu
      ; HKLM install path matches our INSTDIR so uninstall
      DeleteRegKey HKLM ${PRODUCT_REG_KEY}
      DeleteRegKey HKLM "${PRODUCT_UNINSTALL_KEY}"
      DeleteRegKey HKLM "${HKLM_APP_PATHS_KEY}"
      ; Sets start menu and desktop scope to all users..
      SetShellVarContext "all"

  cont_uninstall:
    
    ; Shortcuts..
    Delete "$DESKTOP\fwbackups.lnk"
    SetShellVarContext all
    Delete "$SMPROGRAMS\fwbackups.lnk"
    SetShellVarContext current

    Goto done

  cant_uninstall:
    MessageBox MB_OK $(lng_un.UninstallCannotUninstall) /SD IDOK
    Quit

  no_rights:
    MessageBox MB_OK $(lng_un.UninstallNoRights) /SD IDOK
    Quit

  done:
SectionEnd ; end of uninstall section

;--------------------------------
;Descriptions
  ;Language strings
  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT SecGtk $(lng_GtkRuntimeDesc)
  !insertmacro MUI_DESCRIPTION_TEXT SecPython $(lng_PythonDesc)
  !insertmacro MUI_DESCRIPTION_TEXT SecPyCron $(lng_PyCronDesc)
  !insertmacro MUI_DESCRIPTION_TEXT SecPyModules $(lng_PyModulesDesc)
  !insertmacro MUI_DESCRIPTION_TEXT Secfwbackups $(lng_fwbackupsPackageDesc)
  !insertmacro MUI_DESCRIPTION_TEXT SecShortcuts $(lng_ShortcutDesc)
  !insertmacro MUI_DESCRIPTION_TEXT SecDesktopShortcut $(lng_ShortcutDesc)
  !insertmacro MUI_DESCRIPTION_TEXT SecStartMenuShortcut $(lng_ShortcutDesc)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Functions
!macro CheckUserInstallRightsMacro UN
  Function ${UN}CheckUserInstallRights
    Push $0
    Push $1
    ClearErrors
    UserInfo::GetName
    IfErrors Win9x
    Pop $0
    UserInfo::GetAccountType
    Pop $1

    StrCmp $1 "Admin" 0 +3
      StrCpy $1 "HKLM"
      Goto done
    StrCmp $1 "Power" 0 +3
      StrCpy $1 "HKLM"
      Goto done
    StrCmp $1 "User" 0 +3
      StrCpy $1 "HKCU"
      Goto done
    StrCmp $1 "Guest" 0 +3
      StrCpy $1 "NONE"
      Goto done
    ; Unknown error
    StrCpy $1 "NONE"
    Goto done

    Win9x:
      StrCpy $1 "HKLM"

    done:
      Exch $1
      Exch
      Pop $0
  FunctionEnd
!macroend
!insertmacro CheckUserInstallRightsMacro ""
!insertmacro CheckUserInstallRightsMacro "un."

;
; Usage:
;   Push $0 ; Path string
;   Call VerifyDir
;   Pop $0 ; 0 - Bad path  1 - Good path
;
Function VerifyDir
  Exch $0
  Push $1
  Push $2
  Loop:
    IfFileExists $0 dir_exists
    StrCpy $1 $0 ; save last
    ${GetParent} $0 $0
    StrLen $2 $0
    ; IfFileExists "C:" on xp returns true and on win2k returns false
    ; So we're done in such a case..
    IntCmp $2 2 loop_done
    ; GetParent of "C:" returns ""
    IntCmp $2 0 loop_done
    Goto Loop

  loop_done:
    StrCpy $1 "$0\fwbackupsFooB"
    ; Check if we can create dir on this drive..
    ClearErrors
    CreateDirectory $1
    IfErrors DirBad DirGood

  dir_exists:
    ClearErrors
    FileOpen $1 "$0\fwbackupsfoo.bar" w
    IfErrors PathBad PathGood

    DirGood:
      RMDir $1
      Goto PathGood1

    DirBad:
      RMDir $1
      Goto PathBad1

    PathBad:
      FileClose $1
      Delete "$0\fwbackupsfoo.bar"
      PathBad1:
      StrCpy $0 "0"
      Push $0
      Goto done

    PathGood:
      FileClose $1
      Delete "$0\fwbackupsfoo.bar"
      PathGood1:
      StrCpy $0 "1"
      Push $0

  done:
  Exch 3 ; The top of the stack contains the output variable
  Pop $0
  Pop $2
  Pop $1
FunctionEnd

Function .onVerifyInstDir
  Push $0
  Push $INSTDIR
  Call VerifyDir
  Pop $0
  StrCmp $0 "0" 0 dir_good
  Pop $0
  Abort

  dir_good:
  Pop $0
FunctionEnd

;
; Usage:
; Call DoWeNeedGtk
; First Pop:
;   0 - We have the correct version
;       Second Pop: Key where Version was found
;   1 - We have an old version that should work, prompt user for optional upgrade
;       Second Pop: HKLM or HKCU depending on where GTK was found.
;   2 - We have an old version that needs to be upgraded
;       Second Pop: HKLM or HKCU depending on where GTK was found.
;   3 - We don't have Gtk+ at all
;       Second Pop: "NONE, HKLM or HKCU" depending on our rights..
;
Function DoWeNeedGtk
  ; Logic should be:
  ; - Check what user rights we have (HKLM or HKCU)
  ;   - If HKLM rights..
  ;     - Only check HKLM key for GTK+
  ;       - If installed to HKLM, check it and return.
  ;   - If HKCU rights..
  ;     - First check HKCU key for GTK+
  ;       - if good or bad exists stop and ret.
  ;     - If no hkcu gtk+ install, check HKLM
  ;       - If HKLM ver exists but old, return as if no ver exits.
  ;   - If no rights
  ;     - Check HKLM
  Push $0
  Push $1
  Push $2
  Push $3

  Call CheckUserInstallRights
  Pop $1
  StrCmp $1 "HKLM" check_hklm
  StrCmp $1 "HKCU" check_hkcu check_hklm
    check_hkcu:
      ReadRegStr $0 HKCU ${GTK_REG_KEY} "Version"
      StrCpy $2 "HKCU"
      StrCmp $0 "" check_hklm have_gtk

    check_hklm:
      ReadRegStr $0 HKLM ${GTK_REG_KEY} "Version"
      StrCpy $2 "HKLM"
      StrCmp $0 "" no_gtk have_gtk

  have_gtk:
    ; GTK+ is already installed; check version.
    ; Change this to not even run the GTK installer if this version is already installed.
    ${VersionCompare} ${GTK_INSTALL_VERSION} $0 $3
    IntCmp $3 1 +1 good_version good_version
    ${VersionCompare} ${GTK_MIN_VERSION} $0 $3

      ; Bad version. If hklm ver and we have hkcu or no rights.. return no gtk
      StrCmp $1 "NONE" no_gtk ; if no rights.. can't upgrade
      StrCmp $1 "HKCU" 0 +2   ; if HKLM can upgrade..
      StrCmp $2 "HKLM" no_gtk ; have hkcu rights.. if found hklm ver can't upgrade..
      Push $2
      IntCmp $3 1 +3
        Push "1" ; Optional Upgrade
        Goto done
        Push "2" ; Mandatory Upgrade
        Goto done

  good_version:
    StrCmp $2 "HKLM" have_hklm_gtk have_hkcu_gtk
      have_hkcu_gtk:
        ; Have HKCU version
        ReadRegStr $0 HKCU ${GTK_REG_KEY} "Path"
        Goto good_version_cont

      have_hklm_gtk:
        ReadRegStr $0 HKLM ${GTK_REG_KEY} "Path"
        Goto good_version_cont

    good_version_cont:
      Push $0  ; The path to existing GTK+
      Push "0"
      Goto done

  no_gtk:
    Push $1 ; our rights
    Push "3"
    Goto done

  done:
  ; The top two items on the stack are what we want to return
  Exch 4
  Pop $1
  Exch 4
  Pop $0
  Pop $3
  Pop $2
FunctionEnd

Function .onInit
  Push $R0
  Push $R1
  Push $R2
  Pop $R0
  StrCpy $name "fwbackups ${PRODUCT_VERSION}"

  ClearErrors
  ReadRegStr $R0 HKCU "${PRODUCT_REG_KEY}" "Installer Language"
  IfErrors 0 +1
  WriteRegStr HKCU "${PRODUCT_REG_KEY}" "Installer Language" "$R0"
  ClearErrors
  StrCpy $ISSILENT "/NOUI"

  ; GTK installer has two silent states.. one with Message boxes, one without
  ; If fwbackups installer was run silently, we want to suppress gtk installer msg boxes.
  IfSilent 0 set_gtk_normal
      StrCpy $ISSILENT "/S"
  set_gtk_normal:

  ${GetParameters} $R0
  ClearErrors
  ${GetOptions} "$R0" "/L=" $R1
  IfErrors +3
  StrCpy $LANGUAGE $R1
  Goto skip_lang

  ; Select Language
    ; Display Language selection dialog
    !insertmacro MUI_LANGDLL_DISPLAY
    skip_lang:

  ClearErrors
  ${GetOptions} "$R0" "/DS=" $R1
  ;IfErrors +7
  ;SectionGetFlags ${SecDesktopShortcut} $R2
  ;StrCmp "1" $R1 0 +2
  ;IntOp $R2 $R2 | ${SF_SELECTED}
  ;StrCmp "0" $R1 0 +3
  ;IntOp $R1 ${SF_SELECTED} ~
  ;IntOp $R2 $R2 & $R1
  ;SectionSetFlags ${SecDesktopShortcut} $R2

  ClearErrors
  ${GetOptions} "$R0" "/SMS=" $R1
  ;IfErrors +7
  ;SectionGetFlags ${SecStartMenuShortcut} $R2
  ;StrCmp "1" $R1 0 +2
  ;IntOp $R2 $R2 | ${SF_SELECTED}
  ;StrCmp "0" $R1 0 +3
  ;IntOp $R1 ${SF_SELECTED} ~
  ;IntOp $R2 $R2 & $R1
  ;SectionSetFlags ${SecStartMenuShortcut} $R2

  ; If install path was set on the command, use it.
  StrCmp $INSTDIR "" 0 instdir_done

  ;  If fwbackups is currently installed, we should default to where it is currently installed
  ClearErrors
  ReadRegStr $INSTDIR HKCU "${PRODUCT_REG_KEY}" ""
  IfErrors +2
  StrCmp $INSTDIR "" 0 instdir_done
  ClearErrors
  ReadRegStr $INSTDIR HKLM "${PRODUCT_REG_KEY}" ""
  IfErrors +2
  StrCmp $INSTDIR "" 0 instdir_done

  Call CheckUserInstallRights
  Pop $R0

  StrCmp $R0 "HKLM" 0 user_dir
    StrCpy $INSTDIR "$PROGRAMFILES\fwbackups"
    Goto instdir_done
  user_dir:
    Push $SMPROGRAMS
    ${GetParent} $SMPROGRAMS $R2
    ${GetParent} $R2 $R2
    StrCpy $INSTDIR "$R2\fwbackups"

  instdir_done:
;LogSet on
  Pop $R2
  Pop $R1
  Pop $R0
FunctionEnd

Function un.onInit 
  StrCpy $name "fwbackups ${PRODUCT_VERSION}"

  ; Get stored language preference
  !insertmacro MUI_UNGETLANGUAGE

FunctionEnd

Function preWelcomePage
  Push $R0

  Push $R1
  Push $R2

  ; Make the GTK+ Section RO if it is required.
  Call DoWeNeedGtk
  Pop $R0
  Pop $R2
  IntCmp $R0 1 gtk_not_mandatory gtk_not_mandatory
    !insertmacro SetSectionFlag SecGtk ${SF_RO}
  gtk_not_mandatory:

  ; If on Win95/98/ME warn them that the GTK+ version wont work
  ${Unless} ${IsNT}
    !insertmacro UnselectSection SecGtk
    !insertmacro SetSectionFlag SecGtk ${SF_RO}
    MessageBox MB_OK $(lng_GtkWindowsIncompatible) /SD IDOK
    IntCmp $R0 1 done done ; Upgrade isn't optional - abort if we don't have a suitable version
    Quit
  ${EndIf}

  done:
  Pop $R2
  Pop $R1
  Pop $R0
FunctionEnd

Function preGtkDirPage
  Push $R0
  Push $R1
  Call DoWeNeedGtk
  Pop $R0
  Pop $R1

  IntCmp $R0 2 +2 +2 no_gtk
  StrCmp $R0 "3" no_gtk no_gtk

  ; Don't show dir selector.. Upgrades are done to existing path..
  Pop $R1
  Pop $R0
  Abort

  no_gtk:
    StrCmp $R1 "NONE" 0 no_gtk_cont
      ; Got no install rights..
      Pop $R1
      Pop $R0
      Abort
    no_gtk_cont:
      ; Suggest path..
      StrCmp $R1 "HKCU" 0 hklm1
        ${GetParent} $SMPROGRAMS $R0
        ${GetParent} $R0 $R0
        StrCpy $R0 "$R0\GTK\2.0"
        Goto got_path
      hklm1:
        StrCpy $R0 "${GTK_DEFAULT_INSTALL_PATH}"

   got_path:
     StrCpy $name "GTK+ ${GTK_INSTALL_VERSION}"
     StrCpy $GTK_FOLDER $R0
     ;!insertmacro install_win32 
     Pop $R1
     Pop $R0
FunctionEnd

Function postGtkDirPage
  Push $R0
  StrCpy $name "fwbackups ${PRODUCT_VERSION}"
  Push $GTK_FOLDER
  Call VerifyDir
  Pop $R0
  StrCmp $R0 "0" 0 done
    MessageBox MB_OK $(lng_GtkBadInstallPath) /SD IDOK
    Pop $R0
    Abort
  done:
  Pop $R0
FunctionEnd
