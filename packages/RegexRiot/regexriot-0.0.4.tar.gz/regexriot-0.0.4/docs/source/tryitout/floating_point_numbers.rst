`Floating point numbers`_
=========================
.. _Floating point numbers: http://regextutorials.com/excercise.html?Floating%20point%20numbers

Match numbers containing floating point. Skip those that don't.

.. code-block::
    :linenos:

    Speed of light in vacuum 299792458 m/s
    Standard atmosphere 101325 Pa
    Earth to sun distance 149600000 km
    Acceleration of gravity 9.80665 m/s^2
    Circumference to diameter ratio 3.141592
    Gas constant 8.3144621 J/mol*K

Pass a RiotExpression into ``qFloatingPointNumbers(...)``

.. raw:: html

    <iframe
    src="../demo/repl/?toolbar=1&kernel=python&code=from RegexRiot import *%0Afrom RegexTutorialsExamples import *%0Ars = None%0AqFloatingPointNumbers(rs)"
    width="100%"
    height="300"
    ></iframe>

.. raw:: html

    <details>
    <summary>Answer</summary>
    <code>one_or_more(DIGIT).then(DOT).then(one_or_more(DIGIT))</code>
    </details>
