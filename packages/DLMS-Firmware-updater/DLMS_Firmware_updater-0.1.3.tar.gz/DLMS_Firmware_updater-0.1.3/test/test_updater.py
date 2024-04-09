import unittest
from src import main


class TestType(unittest.TestCase):
    def test_connect(self):
        main.main()
