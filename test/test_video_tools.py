from unittest import TestCase
from PyVideoEditor.video_tools import TimelineMarks

class TestVideoTools(TestCase):

    def test_duration(self):
        timeline_marks = TimelineMarks()
        timeline_marks.reset(60000)
        self.assertEqual(timeline_marks.duration(), 60000)
        timeline_marks.mark_in = 1000
        timeline_marks.mark_out = 11000
        self.assertEqual(timeline_marks.duration(), 10000)
        timeline_marks.mark_in = -1
        self.assertEqual(timeline_marks.duration(), 11000)
        timeline_marks.mark_in = 1000
        timeline_marks.mark_out = -1
        self.assertEqual(timeline_marks.duration(), 59000)

    def test_current_range(self):
        timeline_marks = TimelineMarks()
        self.assertEqual(timeline_marks.current_range(), "---")
        timeline_marks.reset(60000)
        self.assertEqual(timeline_marks.current_range(), "00:00:00.000 - 00:01:00.000")
        timeline_marks.mark_in = 1000
        timeline_marks.mark_out = 11000
        self.assertEqual(timeline_marks.current_range(), "00:00:01.000 - 00:00:11.000")
        timeline_marks.mark_in = -1
        self.assertEqual(timeline_marks.current_range(), "00:00:00.000 - 00:00:11.000")
        timeline_marks.mark_in = 1000
        timeline_marks.mark_out = -1
        self.assertEqual(timeline_marks.current_range(), "00:00:01.000 - 00:01:00.000")
    
    def test_milliseconds_to_timecode(self):
        self.assertEqual(TimelineMarks.milliseconds_to_timecode(1000), "00:00:01.000")
        self.assertEqual(TimelineMarks.milliseconds_to_timecode(0), "00:00:00.000")
        self.assertEqual(TimelineMarks.milliseconds_to_timecode(4530000), "01:15:30.000")


if __name__ == '__main__':
    from unittest import main
    main()
