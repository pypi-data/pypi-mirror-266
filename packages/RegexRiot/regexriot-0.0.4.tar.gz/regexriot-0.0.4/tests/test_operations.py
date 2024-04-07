from src.RegexRiot import *
import unittest

class RiotOperationsString(unittest.TestCase):
    """
    These tests will check that the RiotStrings are forming correctly.
    Another set of tests will check wheter the RiotString match correctly.
    
    """

    def test_then(self):
        self.assertEqual(str(DIGIT.then(NON_ALPHANUM)), r'\d\W')
    
    def test_one_or_more(self):
        self.assertEqual(str(DIGIT.one_or_more()), r'\d+')
        self.assertEqual(str(riot('hello').one_or_more()), r'(hello)+')
        self.assertEqual(str(one_or_more(DIGIT)), r'\d+')
        self.assertEqual(str(one_or_more(riot('hello'))), r'(hello)+')

    def test_one_or_more_around_then(self):
        self.assertEqual(str(one_or_more(DIGIT.then(ALPHANUM))), r'(\d\w)+')
