PyCoffer Long Time Backup
============================

What is a Long Time Backup ?

Just a backup that you can recover in a long time :)

Imagine yourself years from now, after a flood, a tornado, a fire ...
a crash or bankruptcy of your email host, your cloud host ...

How to get your digital life (and your normal life) back ?

PyCoffer LTB can help you :)

LTB are only a secure and durable way to safeguard your personal information.

Let's test this experimental feature.

Today
---------

Using `nuitka <https://nuitka.net/>`_, it's possible to make a binary of
PyCoffer.

.. code::

    ./static.sh

This will create a venv, install all required packages and make a binary.
After some time, the build finish :

.. code::

    Nuitka: Removing dist folder 'pycoffer_static.dist'.
    Nuitka: Removing build directory 'pycoffer_static.build'.
    Nuitka: Successfully created 'pycoffer_static.bin'.

.. code::

    ls -lisak pycoffer_static.bin

.. code::

    ... -rwxrwxr-x 1 ... pycoffer_static.bin

Test it :

.. code::

    ./pycoffer_static.bin check system

.. code::

    Cryptors : ['NaclCryptor', 'FernetCryptor', 'AesCryptor']
    Coffers : ['CofferBank', 'CofferMarket', 'CofferNull', 'CofferStore']
    Plugins : ['Crypt', 'Password', 'Rsync']
    Python : 3.12.9 (CPython)
    Architecture : Linux (6.8.0-52-generic) / x86_64
    System : #53~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Wed Jan 15 19:18:46 UTC 2
    Os : Ubuntu 22.04.5 LTS \n \l
    Specific : ('glibc', '2.35')
    Ldd : ['linux-vdso.so.1 (0x00007fff523f5000)', 'libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007a3e47200000)', '/lib64/ld-linux-x86-64.so.2 (0x00007a3e47559000)']

You can see all informations above ? ok ... your binary is Ok.

.. code::

    ldd pycoffer_static.bin

.. code::

    linux-vdso.so.1 (0x00007ffcd92ad000)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x0000714a0c400000)
    /lib64/ld-linux-x86-64.so.2 (0x0000714a0c80a000)

As you can see, pycoffer_static.bin is still linked to libc.

Generate an info file :

.. code::

    ./pycoffer_static.bin check system >pycoffer_static.bin.infos

Copy your coffer(s), the pycoffer_static.bin binary file and the
pycoffer_static.bin.infos file on a USB card.

Copy your keys (or configuration file) to another support.

In 2075
---------------

Now, we are in 2075 and you need to recover your digital life ...
From 2025

First of all... why 2025???
ok ok ok... you made backups but you lost them

As we notice before, pycoffer_static.bin is linked to libc ...
so you need a compatible release of libc to launch it.

Let's try with current Linux distro and hope for a miracle :)

But not need to wait a miracle, just need to find an install CD
or more simple a docker image of a compatible libc.
