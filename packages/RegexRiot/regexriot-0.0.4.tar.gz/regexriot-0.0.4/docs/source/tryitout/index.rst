Try it out
==========
Try using RegexRiot. I promise you'll like it.

Interactive Repl
----------------

Press the ▶️ button or hit [shift+enter] to run your code.

.. raw:: html

    <iframe
    src="../demo/repl/?toolbar=1&kernel=python&code=from RegexRiot import *"
    width="100%"
    height="300"
    ></iframe>

`Basic Expressions`_
--------------------
.. _Basic Expressions: RegexRiot/BasicExpressions.html

``RegexRiot`` gives you a slew of basic expressions from which you can build out 
any more complicated expression. 

- ``ALPHANUM`` | ``NON_ALPHANUM``
- ``ANYTHING``
- ``BEGINING`` | ``END``
- ``BOUNDARY`` | ``NON_BOUNDARY``
- ``DIGIT`` | ``NON_DIGIT``
- ``DOT`` 
- ``SPACE``
- ``OPEN_PARENTHESIS`` | ``CLOSE_PARENTHESIS``

Try entering some of them in the `Interactive Repl`_.

Chaining Operations
-------------------
Once you have simple RiotExpressions, you can modify and chain them together 
with methods like

- ``one_or_more(DIGIT)``
- ``DIGIT.then(DOT)``

Try using this in the `Interactive Repl`_.

I'm still developing this library so expect the operations to become more 
capable over time.

.. toctree::
    :hidden:

    floating_point_numbers
    years_before_1990

REGEXTUTORIALS
-----------------
`REGEXTUTORIALS`_ has bunch of exercises which I used to learn and grow 
comfortable with regex. So in the following pages you can try your hand at using 
RegexRiot to solve excercise.

.. _REGEXTUTORIALS: http://regextutorials.com


