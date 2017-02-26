# -*- coding: utf-8 -*-

from .subtitletime import SubtitleTime
from .config import *

#
# Subtitle Sentence
#
class SubtitleSentence (object):
    def __init__(self, id, start_hours, start_minutes, start_seconds, start_milliseconds,
                 end_hours, end_minutes, end_seconds, end_milliseconds, sentence):
        self.id = id
        self.start = SubtitleTime(start_hours, start_minutes, start_seconds, start_milliseconds)
        self.end = SubtitleTime(end_hours, end_minutes, end_seconds, end_milliseconds)
        self.sentence = sentence

    @staticmethod
    def fromMatch(match):
        return SubtitleSentence(
            match.group('id'),
            match.group('start_hours'),
            match.group('start_minutes'),
            match.group('start_seconds'),
            match.group('start_milliseconds'),
            match.group('end_hours'),
            match.group('end_minutes'),
            match.group('end_seconds'),
            match.group('end_milliseconds'),
            match.group('sentence').strip()
        )

    def __str__(self):
        return unicode(
            "{}\r\n"
            "{} --> {}\r\n"
            "{}\r\n\n"
        ).format(self.id, self.start, self.end, self.sentence).encode(SUBTITLES_ENCODING)

    def __repr__(self):
        return self.__str__()
