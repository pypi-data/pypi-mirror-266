import unittest
from src.PREN_flawas import Energy

class testEnergy(unittest.TestCase):

    def testCheckCloudStatus(self):
        url = "https://shelly-21-eu.shelly.cloud/device/status"
        id = "30c6f789ee2c"
        auth_key = "M2E4MTZ1aWQ3B6E29EC6B2F2E6CA701201ED69A80FC1CD43D464627AE62B1DEB3E5307D17935ADC8D5A75A3EEC8"
        self.assertTrue(Energy.checkCloudStatus(url))

if __name__ == '__main__':
    unittest.main()
