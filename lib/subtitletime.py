# -*- coding: utf-8 -*-

import re, math

#
# Subtitle Time
#
class SubtitleTime (object):
    def __init__(self, hours, minutes, seconds, milliseconds):
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(seconds)
        self.milliseconds = int(milliseconds)

    def toMilliseconds(self):
        ms = self.hours * 60000 * 60
        ms += self.minutes * 60000
        ms += self.seconds * 1000
        ms += self.milliseconds
        return ms

    def __str__(self):
        hours = '0{}'.format(self.hours) if self.hours < 10 else '{}'.format(self.hours)
        minutes = '0{}'.format(self.minutes) if self.minutes < 10 else '{}'.format(self.minutes)
        seconds = '0{}'.format(self.seconds) if self.seconds < 10 else '{}'.format(self.seconds)
        if self.milliseconds < 10:
            milliseconds = '00{}'.format(self.milliseconds)
        elif self.milliseconds < 100:
            milliseconds = '0{}'.format(self.milliseconds)
        else:
            milliseconds = '{}'.format(self.milliseconds)
        return unicode('{}:{}:{},{}').format(hours, minutes, seconds, milliseconds)

    @staticmethod
    def fromString(string):
        match = re.search(
            '(?P<hours>([0-9]{2}))\:(?P<minutes>([0-9]{2}))\:(?P<seconds>([0-9]{2}))\,(?P<milliseconds>([0-9]{3}))',
            string, re.DOTALL)
        if not match:
            raise Exception('"{}" is not a valid SubtitleTime format.'.format(string))
        return SubtitleTime(
            match.group('hours'),
            match.group('minutes'),
            match.group('seconds'),
            match.group('milliseconds')
        )

    @staticmethod
    def fromShift(value, identifier):
        value = int(value)
        validIdentifiers = ['ms', 's', 'm']
        hours, minutes, seconds, milliseconds = 0, 0, 0, 0
        if identifier not in validIdentifiers:
            raise Exception(
                'bad identifer "{}", must be one of "{}".'.format(identifier, ', '.join(validIdentifiers)))
        if identifier == 'm':
            if value > 59:
                hours = math.floor(value / 60)
                minutes = value - (hours * 60)
            else:
                minutes = value
        elif identifier == 's':
            if value > 59:
                minutes = math.floor(value / 60)
                if minutes > 59:
                    hours = math.floor(minutes / 60)
                    minutes = minutes - (hours * 60)
                seconds = value - (minutes * 60)
            else:
                seconds = value
        elif identifier == 'ms':
            if value > 999:
                seconds = math.floor(value / 1000)
                if seconds > 59:
                    minutes = math.floor(seconds / 60)
                    if minutes > 59:
                        hours = math.floor(minutes / 60)
                        minutes = minutes - (hours * 60)
                    seconds = seconds - (minutes * 60)
                milliseconds = value - (seconds * 1000)
            else:
                milliseconds = value
        return SubtitleTime(
            hours,
            minutes,
            seconds,
            milliseconds
        )

    def sub(self, value, identifier):
        st = SubtitleTime.fromShift(value, identifier)
        self.hours -= st.hours
        self.minutes -= st.minutes
        self.seconds -= st.seconds
        self.milliseconds -= st.milliseconds
        if self.milliseconds < 0:
            self.milliseconds = 1000 - math.fabs(self.milliseconds)
            self.seconds -= 1
        if self.seconds < 0:
            self.seconds = 60 - math.fabs(self.seconds)
            self.minutes -= 1
        if self.minutes < 0:
            self.minutes = 60 - math.fabs(self.minutes)
            self.hours -= 1
        if self.hours < 0:
            raise Exception('Reached negative hours (maybe decreased to low).')
        self.hours = int(self.hours)
        self.minutes = int(self.minutes)
        self.seconds = int(self.seconds)
        self.milliseconds = int(self.milliseconds)

    def add(self, value, identifier):
        st = SubtitleTime.fromShift(value, identifier)
        self.hours += st.hours
        self.minutes += st.minutes
        self.seconds += st.seconds
        self.milliseconds += st.milliseconds
        if self.milliseconds > 999:
            self.milliseconds -= 1000
            self.seconds += 1
        if self.seconds > 59:
            self.seconds -= 60
            self.minutes += 1
        if self.minutes > 59:
            self.minutes -= 60
            self.hours += 1
