from _riot import RiotString

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
'RiotString to match a character at a boundary position. ``\\b``'
NON_BOUNDARY= RiotString(r'\B', "", lambda a,b: a, unit=True)
'RiotString to match a character not at a boundary position. ``\B``'
DOT         = RiotString(r'\.', "", lambda a,b: a, unit=True)
'RiotString to match a dot. ``\.``'
BEGINING    = RiotString(r'^', "", lambda a,b: a, unit=True)
'RiotString to match the begining of a line. ``^``'
END         = RiotString(r'$', "", lambda a,b: a, unit=True)
'RiotString to match the end of a line. ``$``'
OPEN_PARENTHESIS = RiotString(r'\(', "", lambda a,b: a, unit=True)
'RiotString to match an open round parenthesis . ``\(``'
CLOSE_PARENTHESIS = RiotString(r'\)', "", lambda a,b: a, unit=True)
'RiotString to match a close round parenthesis . ``\)``'



