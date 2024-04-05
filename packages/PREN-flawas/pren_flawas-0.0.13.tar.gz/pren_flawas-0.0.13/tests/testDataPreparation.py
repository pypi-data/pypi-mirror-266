import json
import unittest
from time import gmtime, strftime
from src.PREN_flawas import DataPreparation

class testDataPreparation(unittest.TestCase):
    def testSetPos1(self):
        DataPreparation.setPos(1, "Blue")
        self.assertEqual("Blue", DataPreparation.getPos(1))

    def testGetJson(self):
        DataPreparation.setPos(1, "Red")
        DataPreparation.setPos(2, "Yellow")
        DataPreparation.setPos(3, "Blue")
        DataPreparation.setPos(4, "Red")
        DataPreparation.setPos(5, "Yellow")
        DataPreparation.setPos(6, "Yellow")
        DataPreparation.setPos(7, "Red")
        DataPreparation.setPos(8, "")

        data = {'time': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                'config': {"1": "Red", "2": "Yellow", "3": "Blue", "4": "Red", "5": "Yellow", "6": "Yellow", "7": "Red", "8": ""}}
        test = json.dumps(data)
        self.assertEqual(test, DataPreparation.getjson())

    def testGetConfig(self):
        DataPreparation.setPos(1, "Red")
        DataPreparation.setPos(2, "Yellow")
        DataPreparation.setPos(3, "Blue")
        DataPreparation.setPos(4, "Red")
        DataPreparation.setPos(5, "Yellow")
        DataPreparation.setPos(6, "Yellow")
        DataPreparation.setPos(7, "Red")
        DataPreparation.setPos(8, "")
        data = {'config': {"1": "Red", "2": "Yellow", "3": "Blue", "4": "Red", "5": "Yellow", "6": "Yellow", "7": "Red",
                           "8": ""}}
        test = json.dumps(data)
        self.assertEqual(test, DataPreparation.getconfig())

if __name__ == '__main__':
    unittest.main()
