RegexRiot
==============

Start using ``RegexRiot`` by importing its content

.. code:: python

    from RegexRiot import *
    # or
    import RegexRiot as rr

The method to build complicated regex is to start out with simple 
``RiotString``\s and modify them into the desired regex like so

.. code:: python

    DIGIT
    DIGIT.then(ALPHANUM)
    one_or_more(DIGIT.then(ALPHANUM))

Try chaining some ``RiotString``\s together

.. raw:: html

   <iframe
      src="../demo/repl/?toolbar=1&kernel=python&code=from%20RegexRiot%20import%20*%0ADIGIT"
      width="100%"
      height="500"
   ></iframe>

Tree
----

.. toctree::
    :glob:

    *