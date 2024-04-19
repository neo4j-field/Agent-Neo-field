import unittest

from objects.nodes import UserMessage

class TestRating(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_init(self) -> None:
        pass

    def test_bad_init(self) -> None:
        with self.assertRaises(ValueError):
            pass

