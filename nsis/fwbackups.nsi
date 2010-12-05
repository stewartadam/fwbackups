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

;--------------------------------
;Version resource
;Remember the installer name doesn't change when this does
  !define PRODUCT_NAME                    "fwbackups"
;  !define PRODUCT_PREREL                  "rc1"
  !define PRODUCT_VERSION                 "1.43.3"
  !define PRODUCT_PUBLISHER               "Stewart Adam"
  !define PRODUCT_WEB_SITE                "http://www.diffingo.com/opensource"

  VIProductVersion                        "${PRODUCT_VERSION}.0"
  VIAddVersionKey "ProductName"           "${PRODUCT_NAME}"
  VIAddVersionKey "FileVersion"           "${PRODUCT_VERSION} ${PRODUCT_PREREL}"
  VIAddVersionKey "ProductVersion"        "${PRODUCT_VERSION}"
  VIAddVersionKey "LegalCopyright"        "(C) 2005 - 2010 Stewart Adam"
  VIAddVersionKey "FileDescription"       "fwbackups Installer (w/ Requirements)"

;--------------------------------
;General
;--------------------------------
;General
  Name                                    "fwbackups"
  OutFile                                 "fwbackups-1.43.3-Setup.exe"
  InstallDir                              $PROGRAMFILES\fwbackups
  Var name
  SetCompressor /SOLID lzma
  ShowInstDetails show
  ShowUninstDetails show
  !define PRODUCT_REG_KEY                 "SOFTWARE\fwbackups"
  !define PRODUCT_UNINSTALL_KEY           "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\fwbackups"

  !define HKLM_APP_PATHS_KEY              "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\fwbackups-runapp.pyw"
  !define STARTUP_RUN_KEY                 "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
  !define PRODUCT_UNINST_EXE              "fwbackups-uninst.exe"
  !define PYTHON_RUNTIME_INSTALLER        "python-2.6.2.msi"
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
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE           "copying.rtf"
  !insertmacro MUI_PAGE_COMPONENTS
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
;Python Install Section
Section $(lng_Python) SecPython
  ;TODO: Check if already installed; Check upgrade.
  ;TODO: Set the proper Start Menu/Programs target
  ;TODO: Check if msiexec exists and point the user
  ;the Win98/ME, W2K MSI Installer webpage, the links
  ;are in http://www.python.org/download/releases/2.6/
  SetOutPath "$TEMP"
  File "..\..\..\installers\${PYTHON_RUNTIME_INSTALLER}"
  ;Installing
  ExecWait 'msiexec /i "$TEMP\${PYTHON_RUNTIME_INSTALLER}" TARGETDIR="$PROGRAMFILES\Python26" /qb!'
  delete "$TEMP\${PYTHON_RUNTIME_INSTALLER}"
SectionEnd

;--------------------------------
;PyCron Install Section
Section $(lng_PyCron) SecPyCron
  SetOutPath "$INSTDIR"
  File "..\..\..\installers\${PYCRON_INSTALLER}"
  ExecWait $INSTDIR\${PYCRON_INSTALLER}
  delete $INSTDIR\${PYCRON_INSTALLER}
SectionEnd

;--------------------------------
;gtkfiles Install Section
Section $(lng_GtkRuntime) SecGtk
  SectionIn 1 RO
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /r ..\..\..\installers\gtkfiles
SectionEnd ; end of GTK+ section

;--------------------------------
;Python Modules Install Section
Section $(lng_PyModules) SecPyModules
  SectionIn 1 RO
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /r ..\..\..\installers\pythonmodules
SectionEnd

;--------------------------------
;fwbackups Install Section
Section $(lng_fwbackupsPackage) Secfwbackups
  SectionIn 1 RO

  ; Check install rights..
  Call CheckUserInstallRights
  Pop $R0

  StrCmp $R0 "NONE" fwbackups_none
  StrCmp $R0 "HKLM" fwbackups_hklm fwbackups_hkcu

  fwbackups_hklm:
    WriteRegStr HKLM "${HKLM_APP_PATHS_KEY}" "" "$INSTDIR\fwbackups-runapp.pyw"
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
    ; FIXME - This does?
    Goto fwbackups_install_files

  fwbackups_install_files:
    SetOutPath "$INSTDIR"
    ; fwbackups files
    SetOverwrite on
    File ..\AUTHORS
    File ..\ChangeLog
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
    File ..\src\fwbackups\*.py
    SetOutPath "$INSTDIR\fwbackups\operations"
    File ..\src\fwbackups\operations\*.py

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
    Delete $INSTDIR\AUTHORS
    Delete $INSTDIR\ChangeLog
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
    Delete $INSTDIR\*.dll
    RMDir /r $INSTDIR\pythonmodules
    RMDir /r $INSTDIR\gtkfiles
    RMDir /r $INSTDIR\fwbackups
    RMDir /r $INSTDIR\.fwbackups
    Delete $INSTDIR\${PRODUCT_UNINST_EXE}
    RMDir $INSTDIR
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
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} $(lng_PythonDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPyCron} $(lng_PyCronDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtk} $(lng_GtkRuntimeDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPyModules} $(lng_PyModulesDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${Secfwbackups} $(lng_fwbackupsPackageDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} $(lng_ShortcutDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktopShortcut} $(lng_ShortcutDesc)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenuShortcut} $(lng_ShortcutDesc)
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

  ClearErrors
  ${GetOptions} "$R0" "/SMS=" $R1

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
