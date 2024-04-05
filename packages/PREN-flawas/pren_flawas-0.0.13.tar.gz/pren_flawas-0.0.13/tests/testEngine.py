import unittest
from src.PREN_flawas import Engine

class MyTestCase(unittest.TestCase):
    def testConfig(self):
        testarray = [16, 26, 20, 23, 5]
        self.assertEqual(testarray, Engine.AllActors)  # add assertion here


if __name__ == '__main__':
    unittest.main()
