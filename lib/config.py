# -*- coding: utf-8 -*-

import getpass

#
# Configuration
#
SUBTITLES_ENCODING = 'UTF-8-SIG'  # in which encoding subtitles must be converted.
# SUBTITLES_USER = "pi"  # the user who subtitle files should belong to.
# SUBTITLES_GROUP = "shares"  # the group who subtitle files should belong to.
# SUBTITLES_UMASK = 0775  # the umask to apply to subtitle files.

#   The subtitles owner wille be the current user if not defined.
try:
    SUBTITLES_USER
except NameError:
    SUBTITLES_USER = getpass.getuser()

#   The subtitles group wille be the current user group if not defined.
try:
    SUBTITLES_GROUP
except NameError:
    SUBTITLES_GROUP = SUBTITLES_USER

#   The default subtitles umask if not defined.
try:
    SUBTITLES_UMASK
except NameError:
    SUBTITLES_UMASK = 0755
