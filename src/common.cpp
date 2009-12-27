/*  Copyright (C) 2009 Stewart Adam
 *  This file is part of fwbackups.
 
 * fwbackups is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * fwbackups is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 
 * You should have received a copy of the GNU General Public License
 * along with fwbackups; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 * The get_directory() function in this file is derived from the
 * src/config/dirs.c file of the VLC project (also licenced GNU GPLv2+).
 * The authors of and copyright on that file are:
 *   Copyright (C) 2001-2007 the VideoLAN team
 *   Copyright (C) 2007-2008 Rémi Denis-Courmont
 *   Authors: Gildas Bazin <gbazin@videolan.org>
 * Thanks!
 */
#include <QString>
#include <stdlib.h>
#include "common.h"

#if defined (WIN32)
# define _WIN32_IE IE5
# include <w32api.h>
# include <shlobj.h>
#endif

QString join_path(QString path1, QString path2) {
  QString joined = path1;
  if( !path1.endsWith(DIR_SEP) && !path2.startsWith(DIR_SEP) ) {
    // We have a "one" and "two" but need "one/two"
    joined.append(DIR_SEP);
  }
  else if ( path1.endsWith(DIR_SEP) && path2.startsWith(DIR_SEP) ) {
    // We have a path such as "/one/" and "/two"
    path2.remove(0, 1);
  }
  // FIXME: What about drive letters?
  joined.append(path2);
  return joined;
}

QString get_directory(bool b_appdata, bool b_common_appdata) {
  /* FIXME: a full memory page here - quite a waste... */
  static char homedir[PATH_MAX] = "";

#if defined (WIN32)
    wchar_t wdir[PATH_MAX];

    /* Get the "Application Data" folder for the current user */
    if(S_OK == SHGetFolderPathW(NULL, (b_appdata ? CSIDL_APPDATA : (b_common_appdata ? CSIDL_COMMON_APPDATA: CSIDL_PERSONAL)) | CSIDL_FLAG_CREATE,
                                NULL, SHGFP_TYPE_CURRENT, wdir)
                                ) {
      static char appdir[PATH_MAX] = "";
      static char comappdir[PATH_MAX] = "";
      WideCharToMultiByte(CP_UTF8, 0, wdir, -1,
                          b_appdata ? appdir : (b_common_appdata ? comappdir :homedir),
                          PATH_MAX, NULL, NULL);
      return b_appdata ? appdir : (b_common_appdata ? comappdir :homedir);
    }
#else
    (void)b_appdata;
    (void)b_common_appdata;
#endif
  if (!*homedir){
        const char *psz_localhome = getenv("HOME");
#if defined(HAVE_GETPWUID_R)
        char buf[sysconf (_SC_GETPW_R_SIZE_MAX)];
        if (psz_localhome == NULL)
        {
            struct passwd pw, *res;

            if (!getpwuid_r (getuid (), &pw, buf, sizeof (buf), &res) && res)
                psz_localhome = pw.pw_dir;
        }
#endif
        if (psz_localhome == NULL)
            psz_localhome = getenv("TMP");
        if (psz_localhome == NULL)
            psz_localhome = "/tmp";

        const char *uhomedir = psz_localhome;
        strncpy (homedir, uhomedir, sizeof (homedir) - 1);
        homedir[sizeof (homedir) - 1] = '\0';
    }
    return QString(homedir);
}

QString get_home_directory() {
  return get_directory(false, false);
}

QString get_appdata_directory() {
  return get_directory(true, false);
}
