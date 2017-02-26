# -*- coding: utf-8 -*-

import os
import re
from .filemanager import FileManager


#
# File Parser
#
class FileParser (object):
    @staticmethod
    def parse(path, pattern='.*'):

        path = FileManager.resolve(path)
        results = []

        for dirname, dirnames, filenames in os.walk(path):
            dirname = FileManager.resolve(dirname)
            for filename in filenames:
                filename = FileManager.resolve(filename)
                if re.search(pattern, filename):
                    results.append(os.path.join(dirname, filename))

        return results
