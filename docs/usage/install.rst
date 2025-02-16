PyCoffer installation
============================

Install pycoffer, preferably in a virtual environment.

.. code::

    pip install pycoffer[cli]

Create your configuration file with your favorite editor.
It is a classical INI file for the ConfigParser.

.. code::

    vim .pycofferrc

.. code::

    [DEFAULT]
    default_backup = .backup
    default_coffer = confidential
    default_location = ~/
    default_hidden = yes
    default_type = bank

