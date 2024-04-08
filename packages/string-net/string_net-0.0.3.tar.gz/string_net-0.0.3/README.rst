==============
StringNet
==============

Package to take a protein-protein interaction (PPI) network from STRING
and observe the interactions of a given protein with other proteins.

Installation
--------------

.. code-block:: shell

   pip install string_net

Usage
-------

Study, inspect, and watch the interactions of a given protein with other
proteins with which it interacts.

.. code-block:: python

   import string_net # First, choose a protein (there is an input command-line)

   string_net.net()  # To observe the PPI network

   string_net.get_partners()  # To observe a table with scores of interactions

Developing
----------

To install StringNet, along with the tools you need to develop and run
tests, run the following in your virtual environment:

.. code-block:: shell

   pip install string_net[dev]

License
-------

This project is licensed under the MIT License. See the LICENSE file for
more information.

Contact
-------

Leonardo.nossa@icloud.com
