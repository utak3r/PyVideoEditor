"""Various video related tools"""

import math

class TimelineMarks():
    """TimelineMarks holds the in and out marks for the video."""

    def __init__(self):
        self.mark_in = -1
        self.mark_out = -1

    def __repr__(self) -> str:
        return self.timecode_start() + " - " + self.timecode_end()

    def duration(self):
        """ Duration between the marks. """
        duration = 0
        if self.mark_in > -1 and self.mark_out > -1:
            duration = self.mark_out - self.mark_in
        return duration
    
    def reset(self):
        """ Reset marks: set both values to default (-1). """
        self.mark_in = -1
        self.mark_out = -1

    def milliseconds_to_timecode(self, time):
        """ Format given time in ms into a string. """
        timecode = ""
        if time > -1:
            hours = math.floor(time / 3600000)
            minutes = math.floor(time / 60000) - hours*60
            seconds = math.floor(time / 1000) - hours*3600 - minutes*60
            milliseconds = time - hours*3600000 - minutes*60000 - seconds*1000
            timecode = "{:0>2}:{:0>2}:{:0>2}.{:0>3}".format(hours, minutes, seconds, milliseconds)
        return timecode

    def timecode_start(self):
        """ Returns mark in in a timecode format. """
        return self.milliseconds_to_timecode(self.mark_in)
            
    def timecode_end(self):
        """ Returns mark out in a timecode format. """
        return self.milliseconds_to_timecode(self.mark_out)

    def duration_timecode(self):
        """ Returns duration in a timecode formatted string. """
        return self.milliseconds_to_timecode(self.duration())

