import os
import unittest

# Load environment variables from .env if it exists
if os.path.exists('./.env'):
    from dotenv import load_dotenv
    load_dotenv()

class EndpointTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print('Tests started')

    @classmethod
    def tearDownClass(self):
        print('Tests finished')

if __name__ == "__main__":
    unittest.main()
