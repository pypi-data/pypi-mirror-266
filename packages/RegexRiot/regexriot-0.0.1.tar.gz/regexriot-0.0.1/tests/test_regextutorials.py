"""These tests are based on the exercises found on http://regextutorials.com/index.html

"""

from src.regex_riot_rk22000.riot import *
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

    @unittest.expectedFailure
    def test_Hexadecimal_colors(self):
        """
        This test is exercise 2 http://regextutorials.com/excercise.html?Hexadecimal%20colors

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
