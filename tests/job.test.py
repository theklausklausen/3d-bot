from job import *
import unittest
import sys
sys.path.append('src')


class TestJob(unittest.TestCase):
    def test_has_quarter_achieved(self):
        job = Job(completion=25)
        self.assertTrue(job.has_quarter_achieved())

        job = Job(completion=50)
        self.assertTrue(job.has_quarter_achieved())

        job = Job(completion=75)
        self.assertTrue(job.has_quarter_achieved())

        job = Job(completion=100)
        self.assertTrue(job.has_quarter_achieved())

        job = Job(completion=0)
        self.assertFalse(job.has_quarter_achieved())

        job = Job(completion=None)
        self.assertFalse(job.has_quarter_achieved())

    def test_has_paused(self):
        job = Job(state='paused')
        self.assertTrue(job.has_paused())

        job = Job(state='printing')
        self.assertFalse(job.has_paused())

        job = Job(state='paused')
        self.assertTrue(job.has_paused())

        job = Job(state='printing')
        self.assertFalse(job.has_paused())

    def test_has_finished(self):
        job = Job(state='printing')
        self.assertFalse(job.has_finished())

        job = Job(state='done')
        self.assertTrue(job.has_finished())

        job = Job(state='printing')
        self.assertFalse(job.has_finished())

        job = Job(state='done')
        self.assertTrue(job.has_finished())


if __name__ == '__main__':
    unittest.main()
