# -*- coding: utf-8 -*-

import os, re, math, codecs, chardet, shutil
from .config import *
from .fileparser import FileParser
from .filemanager import FileManager
from .subtitlesentence import SubtitleSentence
from .subtitletime import SubtitleTime


#
# Subtitle
#
class Subtitle (object):
    extensionPattern = '.srt$'
    sentencesPattern = (
        '(?P<id>([0-9]+))([\r\n]+)'
        '(?P<start_hours>([0-9]{2}))\:(?P<start_minutes>([0-9]{2}))\:'
        '(?P<start_seconds>([0-9]{2}))\,(?P<start_milliseconds>([0-9]{3}))'
        '\s\-\-\>\s(?P<end_hours>([0-9]{2}))\:(?P<end_minutes>([0-9]{2}))\:'
        '(?P<end_seconds>([0-9]{2}))\,(?P<end_milliseconds>([0-9]{3}))'
        '([\r\n]+)(?P<sentence>(([^\r\n]+[\r\n])+))'
    )
    languages = ['fr', 'en']
    backupFileExtension = '.back'

    def __init__(self, fileName):
        hasValidExtension = lambda f: re.search(Subtitle.extensionPattern, f)
        fileName = FileManager.resolve(fileName)  # resolves escaped spaces causing errors with os.path
        if not os.path.isfile(fileName) or not hasValidExtension(fileName):
            raise Exception('"{}" is not a valid subtitle file.'.format(FileManager.restore(fileName)))
        self._file = fileName
        self._content = None
        self._rawContent = None
        self._encoding = None
        self._hasBackup = None

    def __str__(self):
        return (
            "File: \"{}\"\n"
            "Encoding: \"{}\"\n"
            "Has backup: \"{}\"\n"
            "Total sentences: {}\n"
            "First sentence: \n\"{}\"\n"
            "Last sentence: \n\"{}\"\n"
        ).format(
            self._file,
            self.getEncoding(),
            self.hasBackup(),
            self.getTotalSentences(),
            str(self.getSentenceAt(0)).strip(),
            str(self.getSentenceAt(-1)).strip()
        )

    def getSentenceAt(self, index):
        return self.getContent()[index]

    def getTotalSentences(self):
        return len(self.getContent())

    def getRawContent(self, refresh=False):
        if refresh is True:
            rawContent = unicode("")
            for sentence in self.getContent():
                rawContent += str(sentence).decode(SUBTITLES_ENCODING)
            self._rawContent = rawContent
            self._content = None
        elif self._rawContent is None:
            if not os.path.isfile(self._file):
                raise Exception('unable to load file "{}"'.format(self._file))
            encoding = self.getEncoding()
            with codecs.open(self._file, mode='rb', encoding=encoding) as content_file:
                content_file.seek(0)
                self._rawContent = content_file.read()
                content_file.flush()
                os.fsync(content_file.fileno())
                content_file.close()
        return self._rawContent

    def getEncoding(self):
        if self._encoding is None:
            content = ''
            with open(self._file, 'r') as subfile:
                subfile.seek(0)
                lines = subfile.readlines(50)
                for line in lines:
                    content += line
                subfile.flush()
                os.fsync(subfile.fileno())
                subfile.close()
            detection = chardet.detect(content)
            self._encoding = detection['encoding']

        return self._encoding

    def getContent(self):
        if self._content is None:
            pattern = re.compile(Subtitle.sentencesPattern, re.DOTALL | re.MULTILINE)
            matches = re.finditer(pattern, self.getRawContent())
            if not matches:
                raise Exception('Could not parse content of "{}".'.format(self._file))
            self._content = []
            for match in matches:
                self._content.append(SubtitleSentence.fromMatch(match))
            if len(self._content) == 0:
                raise Exception('An error occured while parsing content.')
        return self._content

    def hasBackup(self, backupFile=None):
        if self._hasBackup is None or backupFile is not None:
            if backupFile is None:
                backupFile = self.getBackupFile()
            else:
                backupFile = FileManager.resolve(backupFile)
            self._hasBackup = os.path.isfile(backupFile)
        return self._hasBackup

    def getBackupFile(self):
        return self._file + Subtitle.backupFileExtension

    def backup(self, backupFile=None, overwrite=False):
        if self._file is None and (backupFile is None or type(backupFile) is bool):
            raise Exception('Missing file path to write into.')
        if type(backupFile) is bool:
            overwrite = backupFile
            backupFile = self.getBackupFile()
        elif backupFile is None:
            backupFile = self.getBackupFile()
        else:
            backupFile = FileManager.resolve(backupFile)
        if not os.path.isfile(backupFile) or overwrite is True:
            shutil.copy2(self._file, backupFile)
            FileManager.applyRights(backupFile)

    @staticmethod
    def backupFile(subFile, backupFile, force):
        sub = Subtitle(subFile)
        sub.backup(backupFile, force)

    def restore(self, backupFile=None):
        if not self.hasBackup(backupFile):
            raise Exception('No backup file exists for restoring.')
        if backupFile is None:
            backupFile = self.getBackupFile()
        else:
            backupFile = FileManager.resolve(backupFile)
        if self._file != backupFile:
            os.remove(self._file)
            extension = Subtitle.backupFileExtension
            match = re.search(extension + '$', backupFile, re.DOTALL)
            if match:
                renamed = backupFile.replace(extension, '')
                os.rename(backupFile, renamed)

    @staticmethod
    def restoreFile(subFile, backupFile):
        sub = Subtitle(subFile)
        sub.restore(backupFile)

    def save(self, destFile=None, parseContent=False):
        if self._file is None and (destFile is None or type(destFile) is bool):
            raise Exception('Missing file path to write into.')
        if destFile is None:
            destFile = self._file
        elif type(destFile) is bool:
            parseContent = destFile
            destFile = self._file
        else:
            destFile = FileManager.resolve(destFile)
        isSameAsSource = False
        if destFile == self._file:
            isSameAsSource = True
            destFile += '.tmp'
        with open(destFile, 'w') as target:
            target.seek(0)
            target.write(self.getRawContent(parseContent).encode(SUBTITLES_ENCODING))
            target.flush()
            os.fsync(target.fileno())
            target.close()
        FileManager.applyRights(destFile)
        if isSameAsSource:
            before, destFile = destFile, destFile.replace('.tmp', '')
            os.rename(before, destFile)

    @staticmethod
    def check(path, force=False):
        if os.path.isdir(path):
            print 'Scaning directory "{}" for subtitles files to check...'.format(path)
            subtitles = FileParser.parse(path, Subtitle.extensionPattern)
            if len(subtitles):
                for fileName in subtitles:
                    Subtitle.check(fileName)

        elif os.path.isfile(path):
            sub = Subtitle(path)
            encoding = sub.getEncoding()
            if encoding is None:
                raise Exception('Unable to detect encoding for subtitle "{}"'.format(path))
            if not encoding == SUBTITLES_ENCODING or force is True:
                sub.backup()
                sub.save()
        else:
            raise Exception('No such file or directory "{}"'.format(path))

    @staticmethod
    def list(path):
        if os.path.isdir(path):
            print 'Scaning directory "{}" for subtitles files to list...'.format(path)
            subtitles = FileParser.parse(path, Subtitle.extensionPattern)
            if len(subtitles):
                for fileName in subtitles:
                    Subtitle.list(fileName)

        elif os.path.isfile(path):
            print Subtitle(path)
        else:
            raise Exception('No such file or directory "{}"'.format(path))

    def explainAction(self, action, quantifier, unit, operand, startsAt, endsAt):
        if startsAt is not None:
            startsAt = ' from "{}"'.format(startsAt)
        else:
            startsAt = ''
        if endsAt is not None:
            endsAt = ' to "{}"'.format(endsAt)
        else:
            endsAt = ''
        direction = 'up' if operand in ['+', 'p'] else 'down'
        print 'Applying {} {} by {}{}{}{}.'.format(action, direction, quantifier, unit, startsAt, endsAt)

    def shift(self, value, startsAt=None, endsAt=None):
        match = re.search('^(?P<operand>(\-|\+|m|p{0,1}))(?P<quantifier>([0-9]{1,4}))(?P<unit>(m|s|ms))$', value,
                          re.DOTALL)
        if not match:
            raise Exception('bad time value : "{}".'.format(value))
        operand, quantifier, unit = match.group('operand'), int(match.group('quantifier')), match.group('unit')
        if startsAt is not None:
            startsAt = SubtitleTime.fromString(startsAt)
        if endsAt is not None:
            endsAt = SubtitleTime.fromString(endsAt)
        self.explainAction('shift', quantifier, unit, operand, startsAt, endsAt)
        if startsAt is not None:
            startsAt = startsAt.toMilliseconds()
        if endsAt is not None:
            endsAt = endsAt.toMilliseconds()
        for index, sentence in enumerate(self.getContent()):
            s = sentence.start.toMilliseconds()
            if startsAt is not None and s <= startsAt:
                continue
            elif endsAt is not None and s > endsAt:
                break
            else:
                if operand in ['+', 'p']:
                    sentence.start.add(quantifier, unit)
                    sentence.end.add(quantifier, unit)
                else:
                    sentence.start.sub(quantifier, unit)
                    sentence.end.sub(quantifier, unit)

    @staticmethod
    def shiftFile(subFile, value, startsAt, endsAt):
        sub = Subtitle(subFile)
        sub.backup()
        sub.shift(value, startsAt, endsAt)
        sub.save(True)

    def delta(self, value, startsAt=None, endsAt=None):
        match = re.search('^(?P<operand>(\-|\+|m|p{0,1}))(?P<quantifier>([0-9]{1,4}))(?P<unit>(m|s|ms))$', value,
                          re.DOTALL)
        if not match:
            raise Exception('bad time value : "{}".'.format(value))
        operand, quantifier, unit = match.group('operand'), int(match.group('quantifier')), match.group('unit')
        if startsAt is not None:
            startsAt = SubtitleTime.fromString(startsAt)
        if endsAt is not None:
            endsAt = SubtitleTime.fromString(endsAt)
        self.explainAction('delta', quantifier, unit, operand, startsAt, endsAt)
        delta = SubtitleTime.fromShift(quantifier, unit)
        d = delta.toMilliseconds()
        if startsAt is not None:
            startsAt = startsAt.toMilliseconds()
        if endsAt is not None:
            endsAt = endsAt.toMilliseconds()
        lastSentence = self.getSentenceAt(-1)
        l = lastSentence.start.toMilliseconds()
        for index, sentence in enumerate(self.getContent()):
            s = sentence.start.toMilliseconds()
            if startsAt is not None and s <= startsAt:
                continue
            elif endsAt is not None and s > endsAt:
                break
            else:
                p = math.floor((s / l) * 100)
                y = math.floor((d * p) / 100)
                if operand in ['+', 'p']:
                    sentence.start.add(y, 'ms')
                    sentence.end.add(y, 'ms')
                else:
                    sentence.start.sub(y, 'ms')
                    sentence.end.sub(y, 'ms')

    @staticmethod
    def deltaFile(subFile, value, startsAt, endsAt):
        sub = Subtitle(subFile)
        sub.backup()
        sub.delta(value, startsAt, endsAt)
        sub.save(True)
