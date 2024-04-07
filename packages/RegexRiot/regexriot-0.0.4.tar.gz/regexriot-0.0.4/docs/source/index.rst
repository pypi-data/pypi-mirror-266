.. RegexRiot documentation master file, created by
   sphinx-quickstart on Mon Apr  1 18:32:34 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RegexRiot
=====================================

A simple easy to use and read regex maker.

.. raw:: html

   <iframe
      src="demo/repl/?toolbar=1&kernel=python&code=from%20RegexRiot%20import%20*%0Aone_or_more(DIGIT).then(DOT).then(one_or_more(DIGIT))"
      width="100%"
      height="300"
   ></iframe>


See its effectiveness against a few `regex exercises`_ 
.. _regex exercises: tryitout/floating_point_numbers.html

Installation 
------------

RegexRiot can be installed using pip.

.. code::

   pip install RegexRiot

.. toctree::
   :hidden:
   :caption: Quickstart

   tryitout/index


.. toctree::
   :hidden:
   :caption: Modules

   RegexRiot/index
   tests/index

.. toctree::
   :hidden:
   :caption: Extra Stuff

   devlog


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
