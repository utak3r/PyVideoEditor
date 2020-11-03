"""Various video related tools"""

import math

class TimelineMarks():
    """TimelineMarks holds the in and out marks for the video."""

    def __init__(self):
        self.mark_in = -1
        self.mark_out = -1
        self.video_duration = 0

    def __repr__(self) -> str:
        return self.current_range()

    def duration(self):
        """ Duration between the marks. """
        duration = 0
        start = 0
        end = self.video_duration
        if self.mark_in > -1:
            start = self.mark_in
        if self.mark_out > -1:
            end = self.mark_out
        duration = end - start
        return duration
    
    def reset(self, video_duration):
        """ Reset marks. """
        self.mark_in = -1
        self.mark_out = -1
        self.video_duration = video_duration

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
        """ Returns beginning of range in a timecode format. """
        start = 0
        if self.mark_in > -1:
            start = self.mark_in
        return self.milliseconds_to_timecode(start)
            
    def timecode_end(self):
        """ Returns end of range in a timecode format. """
        end = self.video_duration
        if self.mark_out > -1:
            end = self.mark_out
        return self.milliseconds_to_timecode(end)

    def duration_timecode(self):
        """ Returns duration in a timecode formatted string. """
        return self.milliseconds_to_timecode(self.duration())

    def current_range(self):
        """ Range in a text format.
        From mark in to mark out, but if they're not set,
        show full video duration.
        """
        video_range = "---"
        if self.duration() > 0:
            video_range = self.timecode_start() + " - " + self.timecode_end()
        return video_range

    def is_trimmed(self):
        """ Checks if range is not a full video. """
        trimmed = False
        if self.mark_in > -1 or self.mark_out > -1:
            trimmed = True
        return trimmed

