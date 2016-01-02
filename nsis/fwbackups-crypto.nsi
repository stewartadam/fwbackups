; fwbackups-crypto.nsi
; The fwbackups crypto modules installer file

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
  VIAddVersionKey "ProductName"           "${PRODUCT_NAME} cryptography modules"
  VIAddVersionKey "FileVersion"           "${PRODUCT_VERSION} ${PRODUCT_PREREL}"
  VIAddVersionKey "ProductVersion"        "${PRODUCT_VERSION}"
  VIAddVersionKey "LegalCopyright"        "(C) 2005 - 2010 Stewart Adam"
  VIAddVersionKey "FileDescription"       "Includes pycrypto and paramiko for fwbackups"

;--------------------------------
;General
  Name                                    "fwbackups"
  OutFile                                 "fwbackups-cryptography-modules-1.43.3-Setup.exe"
  InstallDir                              $PROGRAMFILES\fwbackups
  Var name
  SetCompressor /SOLID lzma
  ShowInstDetails show
  !define PRODUCT_REG_KEY                 "SOFTWARE\fwbackups"

  !define HKLM_APP_PATHS_KEY              "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\fwbackups-runapp.py"
  !define STARTUP_RUN_KEY                 "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

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
  ;!define MUI_FINISHPAGE_RUN             "$INSTDIR\fwbackups-runapp.py"
  ;!define MUI_FINISHPAGE_RUN_NOTCHECKED
  !define MUI_FINISHPAGE_LINK             $(lng_VisitTheWebsite)
  !define MUI_FINISHPAGE_LINK_LOCATION    "${PRODUCT_WEB_SITE}"

;  !define MUI_WELCOMEFINISHPAGE_BITMAP   ".\pixmaps\pidgin-intro.bmp"

;--------------------------------
;Pages
  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE           "copying-crypto.rtf"
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

;--------------------------------
; Language files
  !include "english.nsh"

;--------------------------------
;fwbackups crypto modules Install Section
Section $(lng_fwbackupsPackage) Secfwbackups
  SectionIn 1 RO
    SetOutPath "$INSTDIR\pythonmodules"
    SetOverwrite on
    File /r ..\..\..\installers\pythonmodules-restricted\*
    SetOutPath "$INSTDIR"
SectionEnd ; end of default fwbackups section

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
  StrCpy $name "fwbackups cryptography modules ${PRODUCT_VERSION}"

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
