import json
import unittest
from src.PREN_flawas import DataVerify


class testDataVerify(unittest.TestCase):
    def testcheckAvailability(self):
        self.assertEqual(True, DataVerify.checkAvailability("http://52.58.217.104:5000/cubes"))

    def testSendStart(self):
        self.assertEqual(True, DataVerify.sendStatus("http://52.58.217.104:5000/cubes/team33/start", "QBg3kjqB59xN"))

    def testSendStatus(self):
        self.assertEqual(True, DataVerify.sendStatus("http://52.58.217.104:5000/cubes/team33/end", "QBg3kjqB59xN"))

    def testSendData(self):
        config = {"1": "red","2": "blue","3": "blue","4": "","5": "yellow","6": "blue","7": "","8": ""}
        time = "2023-09-20 17:10:05"
        self.assertEqual(True, DataVerify.sendData("http://52.58.217.104:5000/cubes/team33/config", "QBg3kjqB59xN", time, config))


if __name__ == '__main__':
    unittest.main()