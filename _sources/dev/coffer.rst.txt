Coffer informations
======================

- The Coffer file is locked.

  By default, reading and writing in the coffer file is done with a filelock.

- The Coffer class is thread-safe.

  For example, you can safely flush coffer from a timer thread.

- Files are encrypted by chunk (64kb by default). You can encrypt large files
  with only small memory amount.

- Read/write in files in Coffer using read, write, readlines and writelines function:

.. code::

    with Coffer( ... ) as store:
        store.write('file.data', data)

- Read/write in files in coffer with context manager:

.. code::

    with Coffer( ... ) as store:
        with store.file('file2.data') as ffile:
            ffile.write(data)

- Access to files with common tar commands:

.. code::

    with Coffer( ... ) as store:
        store.add('/tmp/file.data', 'myfiles/file.data')

    with Coffer( ... ) as store:
        store.extract('myfiles', '/tmp/test')

    with Coffer( ... ) as store:
        store.delete('myfiles/file.data')

- Easely extensible with plugins:

.. code::

    with main_lib.open_coffer(conf, coffer, 'r') as ff:
        with ff.plugin('crypt') as plg:
            plg.encrypt(source, target)

- temp directory : the coffer is extracted in a temp directory
  before accessing to files.

  The default location is the system one.

  You can improve access time to files in the coffer using a dedicated 'temp_dir' in RAM.

- temp directory again :

  The files extracted in temp directory are removing after closing ...

  But while you use them or after an application bug ... they are in /tmp

  This can be a security issue if files are stored in clear in coffer.

  Look at CofferBank which use Fernet to encrypt the coffer file and PyNacl
  to encrypt files inside.

- 'Auto flush' : all writes and deletes to files are flushing to disk,
  that means that a new coffer file is written to disk !!!

  This is safe but slow.

  Sometimes, when you want to create archive of cold datas, you don't need
  to flush on every file update, but only when you close the coffer file.

  Look at CofferStore, it use PyNacl to encrypt the coffer and pyzstd to
  compress (not encrypt) the files inside.

  Or look at CofferMarket, it use PyNacl to encrypt files and pyzstd to
  compress (not encrypt) the coffer.

- For testing, use the CofferNull ... no encryption at all, so you can access
  data with the internal open function.

- Look at https://github.com/bibi21000/PyCoffer/blob/main/BENCHMARK.md to
  choose your coffer.
