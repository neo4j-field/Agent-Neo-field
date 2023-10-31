import sys
# setting path
sys.path.append('/Users/alexandergilmore/Documents/GitHub/Agent-Neo-field/src/main/app')
# print(sys.path)

import unittest
from communicator import Communicator

class testCommunicator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.com = Communicator()
    
    def setUp(self) -> None:
        self.example_question = "What is GDS?"

    def tearDown(self) -> None:
        pass

    def test_encode_texts_to_embeddings(self):
        test_embeddings = self.com.encode_texts_to_embeddings([self.example_question])

        self.assertEqual(len(test_embeddings[0]), 768)

if __name__ == '__main__':
    unittest.main()