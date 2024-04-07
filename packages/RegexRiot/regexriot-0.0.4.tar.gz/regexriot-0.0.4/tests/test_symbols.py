from src.RegexRiot import *
import unittest

class LiteralsStringValueTests(unittest.TestCase):
    
    def test_digit(self):
        self.assertEqual(str(DIGIT), r'\d')
        self.assertEqual(str(NON_DIGIT), r'\D')
    
    def test_anything(self):
        self.assertEqual(str(ANYTHING), r'.')
    
    def test_alphanum(self):
        self.assertEqual(str(ALPHANUM), r'\w')
        self.assertEqual(str(NON_ALPHANUM), r'\W')
        
    def test_space(self):
        self.assertEqual(str(SPACE), r'\s')
        self.assertEqual(str(NON_SPACE), r'\S')
    
    def test_boundary(self):
        self.assertEqual(str(BOUNDARY), r'\b')
        self.assertEqual(str(NON_BOUNDARY), r'\B')
    
    def test_dot(self):
        self.assertEqual(str(DOT), r'\.')
    
    def test_custom_string(self):
        words = ['hello','there', ',', ' ', 'general', 'kenobi']
        for w in words:
            self.assertEqual(str(riot(w)), w)
    
    def test_begining_and_end(self):
        self.assertEqual(str(BEGINING), r'^')
        self.assertEqual(str(END), r'$')
    
    def test_round_parentheses(self):
        self.assertEqual(str(OPEN_PARENTHESIS), r'\(')
        self.assertEqual(str(CLOSE_PARENTHESIS), r'\)')
        
