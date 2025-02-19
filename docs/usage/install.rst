PyCoffer installation
============================

Install pycoffer, preferably in a virtual environment :

.. code::

    pip install pycoffer[cli]

Create your configuration file with your favorite editor.
It is a classical INI file for the ConfigParser.

.. code::

    vim ~/.pycofferrc

.. code::

    [DEFAULT]
    default_backup = .backup
    default_coffer = confidential
    default_location = ~/
    default_hidden = yes
    default_type = bank

Change user rights on that file. Must be only readable and writable by owner :

.. code::

    chmod 600 ~/.pycofferrc

Generate config for your coffer :

.. code::

    pycoffer generate --coffer personal --location ~/.personal.pcof

.. code::

    [personal]
    type = bank
    backup = .backup
    coffer_key = dVEzSkJxQ0o4MzkwRHhSSndiTVNhUUYyT1dtMWxHdjdUdlJYSGs5cEdBZz0=
    secure_key = i2Expb5pIkBdRjI8SGnr3h7MCbnyL0iaycqAJeHZy5k=
    location = /home/<user>/.personal.pcof

Add it to your pycofferrc file :

.. code::

    vim ~/.pycofferrc

It should looks like :

.. code::

    [DEFAULT]
    default_backup = .backup
    default_coffer = confidential
    default_location = ~/
    default_hidden = yes
    default_type = bank

    [personal]
    type = bank
    backup = .backup
    coffer_key = dVEzSkJxQ0o4MzkwRHhSSndiTVNhUUYyT1dtMWxHdjdUdlJYSGs5cEdBZz0=
    secure_key = i2Expb5pIkBdRjI8SGnr3h7MCbnyL0iaycqAJeHZy5k=
    location = /home/<user>/.personal.pcof

Check for default coffer and configuration :

.. code::

    pycoffer add --help

.. code::

    Usage: pycoffer add [OPTIONS]

      Add file/directory in coffer.

    Options:
      -c, --conf TEXT    The pycoffer configuration file.  [default:
                         /home/sebastien/.pycofferrc]
      -f, --coffer TEXT  The coffer name.  [default: personal]
      -s, --source TEXT  The file/directory to add to coffer.
      -t, --target TEXT  The target in coffer. If None, the basename is used.
      --replace          Replace file in coffer if already exists.
      --help             Show this message and exit.

All is correct, you are now ready to use your coffer :

.. code::

    pycoffer add --source README.md

Check file is in coffer :

.. code::

    pycoffer ls

Extract it :

.. code::

    pycoffer extract --file README.md --path test/

Check it is here :

.. code::

    ls test/README.md

Now import your chrome passwords :

.. code::

    pycoffer password import-chrome -i chrome-exported-password.csv

List your password informations in coffer (not show passwords) :

.. code::

    pycoffer password ls

.. code::

    Name Username Url Owner
    127.0.0.1 user1 https://127.0.0.1/ chrome
    example.com user1 https://www.example.com/ chrome
    toto.com user https://www.totoaucongo.com/ chrome
    tata.com user2 https://www.tataenalabama.com/ chrome

Show a password from coffer :

.. code::

    pycoffer password show --name example.com --owner chrome

.. code::

    Owner Name Username Url Password
    chrome example.com user1 https://www.example.com/ azerty

Crypt a file using key from coffer. You need an existing coffer to encrypt external files :

.. code::

    pycoffer crypt --source README.md --target README.md.crypt

.. code::

    Owner Name Username Url Password
    chrome example.com user1 https://www.example.com/ azerty

Crypt a file using key from coffer. You need an existing coffer to encrypt external files :

.. code::

    pycoffer crypt --source README.md --target README.md.crypt

.. code::

    ls README.md*

.. code::

    README.md  README.md.crypt

Finally, you can export all data from your coffer :

.. code::

    pycoffer extract --all --path testall

.. code::

    ls -lisa testall/

.. code::

    .plugins  README.md

You can see a hidden directory .plugins. This is where passwords are saved
in a pickle file.

.. code::

    ls -lisa testall/.plugins

.. code::

    passwd

And now, what to do with your coffer ?

You can safely copy it on cloud or on USB memory card.

As long as you don't copy your keys (or configuration file) on the same
support, your informations are secured.

