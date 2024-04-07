`Years before 1990`_
====================
.. _Years before 1990: http://regextutorials.com/excercise.html?Years%20before%201990

Match titles of all films produced before 1990.

.. code-block::
    :linenos:

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

Pass a RiotExpression into ``qYearsBefore1990(...)``

.. raw:: html

    <iframe
    src="../demo/repl/?toolbar=1&kernel=python&code=from RegexRiot import *%0Afrom RegexTutorialsExamples import *%0Ars = None%0AqYearsBefore1990(rs)"
    width="100%"
    height="300"
    ></iframe>

.. raw:: html

    <details>
    <summary>Answer</summary>
    <code>
        one_or_more(ANYTHING).then(OPEN_PARENTHESIS).then(1).then(DIGIT).then(riot(0, to=8)).then(one_or_more(ANYTHING))
    </code>
    </details>
