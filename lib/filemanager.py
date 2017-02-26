# -*- coding: utf-8 -*-

import os
import pwd
import grp
from .config import *


#
# File Manager
#
class FileManager (object):
    @staticmethod
    def resolve(path):
        return path.replace('\\ ', ' ')  # resolves escaped spaces causing errors with os

    @staticmethod
    def restore(path):
        return path.replace(' ', '\\ ')  # restores escaped spaces causing errors with os

    @staticmethod
    def applyRights(path):
        path = FileManager.resolve(path)
        uid = pwd.getpwnam(SUBTITLES_USER).pw_uid
        gid = grp.getgrnam(SUBTITLES_GROUP).gr_gid
        update = (lambda p: (os.chown(p, uid, gid) and False) or (os.chmod(p, SUBTITLES_UMASK) and False))

        if os.path.isfile(path):
            update(path)

        elif os.path.isdir(path):

            update(path)

            for dirname, dirnames, filenames in os.walk(path):

                for subdirname in dirnames:
                    update(os.path.join(dirname, subdirname))

                for filename in filenames:
                    update(os.path.join(dirname, filename))

        else:
            raise Exception('"{}" is not a valid file or directory.'.format(path))

    @staticmethod
    def createDir(path):
        path = FileManager.resolve(path)
        os.mkdir(path)
        FileManager.applyRights(path)

    @staticmethod
    def remove(path):
        path = FileManager.resolve(path)

        if os.path.isfile(path):
            os.remove(path)

        elif os.path.isdir(path):

            for dirname, dirnames, filenames in os.walk(path, topdown=False):

                dirname = FileManager.resolve(dirname)

                for filename in filenames:
                    os.remove(os.path.join(dirname, filename))

                for subdirname in dirnames:
                    subdirname = FileManager.resolve(subdirname)
                    os.rmdir(os.path.join(dirname, subdirname))

            os.rmdir(path)

        else:
            raise Exception('"{}" is not a valid file or directory.'.format(path))
