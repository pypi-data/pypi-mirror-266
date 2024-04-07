"""These tests are based on the exercises found on http://regextutorials.com/index.html

"""

from src.RegexRiot import *
import unittest
import re

class RegexTutorials(unittest.TestCase):

    def test_Floating_point_numbers(self):
        """
        This test is exercise 1 http://regextutorials.com/excercise.html?Floating%20point%20numbers

        Match numbers containing floating point. Skip those that don't.

        Speed of light in vacuum 299792458 m/s

        Standard atmosphere 101325 Pa
        
        Earth to sun distance 149600000 km
        
        Acceleration of gravity 9.80665 m/s^2
        
        Circumference to diameter ratio 3.141592
        
        Gas constant 8.3144621 J/mol*K

        """
        lines = [
                ["Speed of light in vacuum 299792458 m/s", []],
                ["Standard atmosphere 101325 Pa", []],
                ["Earth to sun distance 149600000 km", []],
                ["Acceleration of gravity 9.80665 m/s^2", ["9.80665"]],
                ["Circumference to diameter ratio 3.141592", ["3.141592"]],
                ["Gas constant 8.3144621 J/mol*K", ["8.3144621"]],
                ]
        pattern = one_or_more(DIGIT).then(DOT).then(one_or_more(DIGIT)).compile()
        for test, matchs in lines:
            self.assertEqual(
                pattern.findall(test),
                matchs
            )
    
    def test_Years_before_1990(self):
        """
        This is exercise 2 http://regextutorials.com/excercise.html?Years%20before%201990

        Match titles of all films produced before 1990.

        1 The Shawshank Redemption (1994)

        2 The Godfather (1972)

        3 The Godfather: Part II (1974)

        4 Pulp Fiction (1994)
        
        5 The Good, the Bad and the Ugly (1966)

        6 The Dark Knight (2008)

        7 12 Angry Men (1957)

        8 Schindler's List (1993)

        9 The Lord of the Rings: The Return of the King (2003)

        10 Fight Club (1999)

        """
        lines = [
            ["1 The Shawshank Redemption (1994)", False],
            ["2 The Godfather (1972)", True],
            ["3 The Godfather: Part II (1974)", True],
            ["4 Pulp Fiction (1994)", False],
            ["5 The Good, the Bad and the Ugly (1966)", True],
            ["6 The Dark Knight (2008)", False],
            ["7 12 Angry Men (1957)", True],
            ["8 Schindler's List (1993)", False],
            ["9 The Lord of the Rings: The Return of the King (2003)", False],
            ["10 Fight Club (1999)", False],
        ]
        pattern = BEGINING.then(one_or_more(ANYTHING)).then(OPEN_PARENTHESIS) \
            .then(1).then(DIGIT).then(riot(0, to=8)).then(DIGIT) \
            .then(CLOSE_PARENTHESIS).compile()

        for l, m in lines:
            self.assertEqual(m, pattern.fullmatch(l) is not None)

    @unittest.expectedFailure
    def test_Hexadecimal_colors(self):
        """
        This test is exercise 3 http://regextutorials.com/excercise.html?Hexadecimal%20colors

        Match 24-bit hexadecimal colors. Skip 12 bit colors.

        24 bit:

        AliceBlue #F0F8FF

        AntiqueWhite #FAEBD7

        Aqua #00FFFF

        Aquamarine #7FFFD4

        Azure #F0FFFF

        12 bit:

        White #FFF

        Red #F00

        Green #0F0

        Blue #00F

        """
        lines = [
                ["24 bit:", []],
                ["AliceBlue #F0F8FF", ["#F0F8FF"]],
                ["AntiqueWhite #FAEBD7", ["#FAEBD7"]],
                ["Aqua #00FFFF", ["#00FFFF"]],
                ["Aquamarine #7FFFD4", ["#7FFFD4"]],
                ["Azure #F0FFFF", ["#F0FFFF"]],
                ["12 bit:", []],
                ["White #FFF", []],
                ["Red #F00", []],
                ["Green #0F0", []],
                ["Blue #00F", []],
            ]
        pattern = RiotString("#").compile()
        for test, matchs in lines:
            self.assertEqual(
                pattern.findall(test),
                matchs
            )
