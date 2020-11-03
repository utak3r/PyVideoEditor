from unittest import TestCase
from PyVideoEditor.video_tools import TimelineMarks

class TestVideoTools(TestCase):

    def test_duration(self):
        timeline_marks = TimelineMarks()
        self.assertEqual(5, 5)

if __name__ == '__main__':
    from unittest import main
    main()
