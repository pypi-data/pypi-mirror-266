import sys
sys.path.append('../google_trendy')

import unittest
from google_trendy import *

class GoogleTrendsTest(unittest.TestCase):
    
    def test_init(self):
        trends = GoogleTrends()
        self.assertIsNotNone(trends)
    
if __name__ == '__main__':
    unittest.main()

