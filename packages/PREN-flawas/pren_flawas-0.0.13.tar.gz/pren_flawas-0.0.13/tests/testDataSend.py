import unittest
from src.PREN_flawas import DataSend


class testDataSend(unittest.TestCase):
    def testcheckAvailability(self):
        DataSend.send("https://i-ba-pren.flaviowaser.ch/upload-data.php", 33, 20)

if __name__ == '__main__':
    unittest.main()
