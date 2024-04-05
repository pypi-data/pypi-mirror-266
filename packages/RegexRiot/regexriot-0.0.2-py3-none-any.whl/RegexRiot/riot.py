"""
This is the primary module in the regex-riot library. Import everything from
this module.

"""

import re
import _operations

class RiotString:
    """
    This is the object that will hold and mutate regular expressions. 
    RiotStrings can be composed together to build more complicated regular 
    expressions. 
    
    For instance the expression ``\d+\.\d+`` can be built using RiotStrings as 
    ``one_or_more(DIGIT).then(DOT).then(one_or_more(DIGIT))``. Although this is 
    not as consice as writing the regex itself, with the help of autocomplete it 
    will be easier to write write regex as a chain of function calls that read
    that read out to english like text.
    
    """

    def __init__(self, a, b, combinator, unit) -> None:
        """Create a RiotString from a given expression. Use this to create a 
        building block from which you will build up to what ever complicated 
        regex you actually want. 
        Something like
        ``RiotString("Annie are you okay ").then("are you okay ").times(2).then("Annie")``
        to make the regex ``"Annie are you okay (are you okay ){2}Annie``
        
        """
        self._a = str(a)
        self._b = str(b)
        self._combinator = combinator
        self._unit = unit

    def __str__(self) -> str:
        return self._combinator(self._a, self._b)
    def __repr__(self) -> str:
        return f'<RiotString: "{str(self)}">'
    
    def then(self, rs):
        """
        The current RiotString followed by the next RiotString. 
        Use like so
        
        ``RiotString('a').then(RiotString('b')) => RiotString('ab')``

        Parameters
        ----------
        rs: The next RiotString or string

        """
        return RiotString(self,rs, _operations.then, False)

    def one_or_more(self):
        """
        The current RiotString repeated one or more times.
        Use like so

        ``one_or_more(RiotString('a')) => RiotString('a+')``
        or
        ``RiotString('a').one_or_more() => RiotString('a+')``

        """
        regex = _operations.one_or_more(self._a, self._unit)
        return RiotString(regex, "", lambda a,b: a, True)
    
    def compile(self) -> re.Pattern:
        """Return the compiled regex. This is the result of ``re.compile("pattern")``"""
        return re.compile(str(self))

one_or_more = RiotString.one_or_more


DIGIT       = RiotString(r'\d', "", lambda a,b: a, unit=True)
'RiotString for a digit. ``\d``'
NON_DIGIT   = RiotString(r'\D', "", lambda a,b: a, unit=True)
'RiotString for non digit. ``\D``'
ANYTHING    = RiotString(r'.', "", lambda a,b: a, unit=True)
'RiotString to match any digit. ``.``'
ALPHANUM    = RiotString(r'\w', "", lambda a,b: a, unit=True)
'RiotString to match any alphanumeric character. ``\w``'
NON_ALPHANUM= RiotString(r'\W', "", lambda a,b: a, unit=True)
'RiotString to match any non-alphanumeric character. ``\W``'
SPACE       = RiotString(r'\s', "", lambda a,b: a, unit=True)
'RiotString to match any space character. ``\s``'
NON_SPACE   = RiotString(r'\S', "", lambda a,b: a, unit=True)
'RiotString to match any non-space character. ``\S``'
BOUNDARY    = RiotString(r'\b', "", lambda a,b: a, unit=True)
'RiotString to match a character at a boundary position. ``\b``'
NON_BOUNDARY= RiotString(r'\B', "", lambda a,b: a, unit=True)
'RiotString to match a character not at a boundary position. ``\B``'
DOT         = RiotString(r'\.', "", lambda a,b: a, unit=True)
'RiotString to match a dot. ``\.``'

def riot(seed):
    """
    Simplified interface for RiotString
    """
    return RiotString(seed, "", lambda a,b: a, len(seed)==1)

