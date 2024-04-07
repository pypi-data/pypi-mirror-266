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
        regex = _operations.one_or_more(str(self), self._unit)
        return RiotString(regex, "", lambda a,b: a, True)
    
    def compile(self) -> re.Pattern:
        """Return the compiled regex. This is the result of ``re.compile("pattern")``"""
        return re.compile(str(self))

one_or_more = RiotString.one_or_more

class RiotSet(RiotString):
    def __init__(self, *args, to=None) -> None:
        self.elements = [str(i) for i in args]
        self.to = str(to)
        if to is not None:
            assert len(args)==1, f"Got multiple arguments for set range start {str(args)}"
            a = f"[{self.elements[0]}-{self.to}]"
        else:
            a = f"[{''.join(self.elements)}]"
        
        super().__init__(a, "", lambda a,b: a, True)


def riot(seed, *args, to=None):
    """
    Simplified interface for RiotString
    """
    if not args and to is None:
        return RiotString(seed, "", lambda a,b: a, len(seed)==1)
    if not to is None:
        assert not args, f"Got extra argument for range start {args}"
        return RiotSet(seed, to=to)
    else:
        return RiotSet(seed, *args)

