; English NSIS translation file for fwbackups installer
; This file is distributed under the GNU GPL
; See COPYING for details
; (C) 2007 Stewart Adam
!insertmacro MUI_LANGUAGE "English"

; Section names
LangString lng_Python ${LANG_ENGLISH} "Python (Required)"
LangString lng_GtkRuntime ${LANG_ENGLISH} "Bundled GTK+ Runtime (Required)"
LangString lng_PyCron ${LANG_ENGLISH} "PyCron (Required)"
LangString lng_PyModules ${LANG_ENGLISH} "Bundled Python modules (Required)"
LangString lng_fwbackupsPackage ${LANG_ENGLISH} "fwbackups (Required)"
LangString lng_HelpFiles ${LANG_ENGLISH} "Help files"
LangString lng_Shortcuts ${LANG_ENGLISH} "Program shortcuts"

; Shortcuts
LangString lng_Desktop ${LANG_ENGLISH} "Desktop"
LangString lng_QuickLaunch ${LANG_ENGLISH} "Quick Launch"
LangString lng_StartMenu ${LANG_ENGLISH} "Start Menu"

; Descriptions
LangString lng_PythonDesc ${LANG_ENGLISH} "The Python interpreted programming language."
LangString lng_GtkRuntimeDesc ${LANG_ENGLISH} "Installs a bundled GTK+ runtime environment for use with fwbackups."
LangString lng_PyCronDesc ${LANG_ENGLISH} "The PyCron Windows service is a cron implementation for Windows written in Python."
LangString lng_PyModulesDesc ${LANG_ENGLISH} "Installs the Python modules (pygtk, pycairo, pygobject) required by fwbackups to function correctly."
LangString lng_fwbackupsPackageDesc ${LANG_ENGLISH} "The fwbackups program files."
LangString lng_HelpFilesDesc ${LANG_ENGLISH} "Additional help files for fwbackups."
LangString lng_ShortcutDesc ${LANG_ENGLISH} "Installs the program shortcuts."

; want to uninstall before install
LangString lng_AlreadyInstalled ${LANG_ENGLISH} "fwbackups has already been installed. Do you want to remove the previous version before installing fwbackups?"

; Other
LangString lng_VisitTheWebsite $(LANG_ENGLISH) "Visit the fwbackups website"

;Uninstall
LangString lng_un.UninstallCannotUninstall $(LANG_ENGLISH) "Setup could not uninstall fwbackups."
LangString lng_un.UninstallNoRights $(LANG_ENGLISH) "You do not have sufficient rights to uninstall fwbackups."


; Languages section
LangString lng_Languages $(LANG_ENGLISH) "Translations"

; Languages section description
;LangString lng_LanguagesDesc $(LANG_ENGLISH) "Install various translations for ${PRODUCT_NAME}"

;LangString lng_am $(LANG_ENGLISH) "am  Amharic"
;LangString lng_az $(LANG_ENGLISH) "az  Azerbaijani"
;LangString lng_be $(LANG_ENGLISH) "be  Byelorussian"
;LangString lng_bg $(LANG_ENGLISH) "bg  Bulgarian"
;LangString lng_bn $(LANG_ENGLISH) "bn  Bengali"
;LangString lng_ca $(LANG_ENGLISH) "ca  Catalan"
;LangString lng_cs $(LANG_ENGLISH) "cs  Czech"
;LangString lng_da $(LANG_ENGLISH) "da  Danish"
;LangString lng_de $(LANG_ENGLISH) "de  German"
;LangString lng_dz $(LANG_ENGLISH) "dz  Dzongkha"
;LangString lng_el $(LANG_ENGLISH) "el  Greek"
;LangString lng_en $(LANG_ENGLISH) "en  English"
;LangString lng_en_AU $(LANG_ENGLISH) "en_AU Australian English"
;LangString lng_en_CA $(LANG_ENGLISH) "en_CA Canadian English"
;LangString lng_en_GB $(LANG_ENGLISH) "en_GB British English"
;LangString lng_en_US@piglatin $(LANG_ENGLISH) "en_US@piglatin Pig Latin"
;LangString lng_eo $(LANG_ENGLISH) "eo  Esperanto"
;LangString lng_es $(LANG_ENGLISH) "es  Spanish"
;LangString lng_es_MX $(LANG_ENGLISH) "es_MX  Mexican Spanish"
;LangString lng_et $(LANG_ENGLISH) "et  Estonian"
;LangString lng_eu $(LANG_ENGLISH) "eu  Basque"
;LangString lng_fi $(LANG_ENGLISH) "fi  Finnish"
;LangString lng_fr $(LANG_ENGLISH) "fr  French"
;LangString lng_ga $(LANG_ENGLISH) "ga  Irish"
;LangString lng_gl $(LANG_ENGLISH) "gl  Gallegan"
;LangString lng_he $(LANG_ENGLISH) "he  Hebrew"
;LangString lng_hr $(LANG_ENGLISH) "hr  Croatian"
;LangString lng_hu $(LANG_ENGLISH) "hu  Hungarian"
;LangString lng_id $(LANG_ENGLISH) "id  Indonesian"
;LangString lng_it $(LANG_ENGLISH) "it  Italian"
;LangString lng_ja $(LANG_ENGLISH) "ja  Japanese"
;LangString lng_km $(LANG_ENGLISH) "km  Khmer"
;LangString lng_ko $(LANG_ENGLISH) "ko  Korean"
;LangString lng_lt $(LANG_ENGLISH) "lt  Lithuanian"
;LangString lng_mk $(LANG_ENGLISH) "mk  Macedonian"
;LangString lng_mn $(LANG_ENGLISH) "mn  Mongolian"
;LangString lng_ne $(LANG_ENGLISH) "ne  Nepali"
;LangString lng_nb $(LANG_ENGLISH) "nb  Norwegian Bokm?l"
;LangString lng_nl $(LANG_ENGLISH) "nl  Dutch"
;LangString lng_nn $(LANG_ENGLISH) "nn  Norwegian Nynorsk"
;LangString lng_pa $(LANG_ENGLISH) "pa  Panjabi"
;LangString lng_pl $(LANG_ENGLISH) "po  Polish"
;LangString lng_pt $(LANG_ENGLISH) "pt  Portuguese"
;LangString lng_pt_BR $(LANG_ENGLISH) "pt_BR Brazilian Portuguese"
;LangString lng_ro $(LANG_ENGLISH) "ro  Romanian"
;LangString lng_ru $(LANG_ENGLISH) "ru  Russian"
;LangString lng_rw $(LANG_ENGLISH) "rw  Kinyarwanda"
;LangString lng_sk $(LANG_ENGLISH) "sk  Slovak"
;LangString lng_sl $(LANG_ENGLISH) "sl  Slovenian"
;LangString lng_sq $(LANG_ENGLISH) "sq  Albanian"
;LangString lng_sr $(LANG_ENGLISH) "sr  Serbian"
;LangString lng_sr@Latn $(LANG_ENGLISH) "sr@Latn  Serbian in Latin script"
;LangString lng_sv $(LANG_ENGLISH) "sv  Swedish"
;LangString lng_th $(LANG_ENGLISH) "th  Thai"
;LangString lng_tr $(LANG_ENGLISH) "tr  Turkish"
;LangString lng_uk $(LANG_ENGLISH) "uk  Ukrainian"
;LangString lng_vi $(LANG_ENGLISH) "vi  Vietnamese"
;LangString lng_zh_CN $(LANG_ENGLISH) "zh_CH  Simplifed Chinese"
;LangString lng_zh_TW $(LANG_ENGLISH) "zh_TW  Traditional Chinese"
