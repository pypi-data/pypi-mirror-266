from RegexRiot import RiotString, END, BEGINING
def showcase(rs:RiotString, lines):
    if rs is None:
        print("You forgot to set `rs` to a Riot Expression")
        print("Feel free to use the hint")
        return
    rs = rs.compile()
    for i, ln in enumerate(lines):
        print(f"{i+1:>3}| {rs.findall(ln)}")

def qFloatingPointNumbers(rs:RiotString=None):
    lines = """
Speed of light in vacuum 299792458 m/s
Standard atmosphere 101325 Pa
Earth to sun distance 149600000 km
Acceleration of gravity 9.80665 m/s^2
Circumference to diameter ratio 3.141592
Gas constant 8.3144621 J/mol*K
    """.strip().split('\n')
    if rs is None: rs = END.then(BEGINING)
    showcase(rs, lines)

def qYearsBefore1990(rs: RiotString):
    lines = """
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
    """.strip().split('\n')
    if rs is None: rs = END.then(BEGINING)
    showcase(rs, lines)