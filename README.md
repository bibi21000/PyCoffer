[![CircleCI](https://dl.circleci.com/status-badge/img/gh/bibi21000/FernetFile/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/bibi21000/FernetFile/tree/main)
[![codecov](https://codecov.io/gh/bibi21000/FernetFile/graph/badge.svg?token=4124GIOJAK)](https://codecov.io/gh/bibi21000/FernetFile)
![PyPI - Downloads](https://img.shields.io/pypi/dm/fernetfile)

# FernetFile

A python xxxFile like (ie TarFile, GzipFile, BZ2File, pyzstd.ZstdFile, ...)
for encrypting files with Fernet.

 - encrypting / decrypting data using chunks to reduce memory footprint
 - chainable with other python xxxFile interfaces (stream mode)
 - interface to compress/encrypt and decrypt/decompress (with pyzstd) in stream mode
 - a FernetStore with a TarFile like interface (work in progress)
 - look at BENCHMARK.md ... and chain :)
 - look at tests for examples


## Install

```
    pip install fernetfile
```

## Create your encryption key

```
    from cryptography.fernet import Fernet

    key = Fernet.generate_key()
```
and store it in a safe place (disk, database, ...).

This key is essential to encrypt and decrypt data.
Losing this key means losing the data.

## "open" your encrypted files like normal files

Text files :

```
    import fernetfile

    with fernetfile.open('test.txc', mode='wt', fernet_key=key, encoding="utf-8") as ff:
        ff.write(data)

    with fernetfile.open('test.txc', "rt", fernet_key=key, encoding="utf-8") as ff:
        data = ff.read()

    with fernetfile.open('test.txc', mode='wt', fernet_key=key, encoding="utf-8") as ff:
        ff.writelines(data)

    with fernetfile.open('test.txc', "rt", fernet_key=key, encoding="utf-8") as ff:
        data = ff.readlines()
```

Binary files :

```
    import fernetfile

    with fernetfile.open('test.dac', mode='wb', fernet_key=key) as ff:
        ff.write(data)

    with fernetfile.open('test.dac', "rb", fernet_key=key) as ff:
        data = ff.read()
```

## Or the fast and furious FernetFile with zstd compression

```
    pip install fernetfile[zstd]
```

```
    from fernetfile.zstd import FernetFile

    with FernetFile('test.dac', mode='wb', fernet_key=key) as ff:
        ff.write(data)

    with FernetFile('test.dac', mode='rb', fernet_key=key) as ff:
        data = ff.read()
```

## And chain it to tar and bz2

```
class TarBz2FernetFile(tarfile.TarFile):

    def __init__(self, name, mode='r', fernet_key=None, chunk_size=fernetfile.CHUNK_SIZE, **kwargs):
        compresslevel = kwargs.pop('compresslevel', 9)
        self.fernet_file = fernetfile.FernetFile(name, mode,
            fernet_key=fernet_key, chunk_size=chunk_size, **kwargs)
        try:
            self.bz2_file = bz2.BZ2File(self.fernet_file, mode=mode,
                compresslevel=compresslevel, **kwargs)
            try:
                super().__init__(fileobj=self.bz2_file, mode=mode, **kwargs)

            except Exception:
                self.bz2_file.close()
                raise

        except Exception:
            self.fernet_file.close()
            raise

    def close(self):
        try:
            super().close()
        finally:
            try:
                if self.fernet_file is not None:
                    self.bz2_file.close()
            finally:
                if self.fernet_file is not None:
                    self.fernet_file.close()

    with TarBz2FernetFile('test.zsc', mode='wb', fernet_key=key) as ff:
        ff.add(dataf1, 'file1.out')
        ff.add(dataf2, 'file2.out')

    with TarBz2FernetFile('test.zsc', mode='rb', fernet_key=key) as ff:
        fdata1 = ff.extractfile('file1.out')
        fdata2 = ff.extractfile('file2.out')
```

## Encrypt / decrypt existing files

Encrypt :
```
    import fernetfile

    with open(source, 'rb') as fin, fernetfile.open(destination, mode='wb', fernet_key=key) as fout:
        while True:
            data = fin.read(7777)
            if not data:
                break
            fout.write(data)
```

Decrypt :
```
    import fernetfile

    with fernetfile.open(source, mode='rb', fernet_key=key) as fin, open(destination, 'wb') as fout :
        while True:
            data = fin.read(8888)
            if not data:
                break
            fout.write(data)
```

Or with the fast and furious FernetFile with zstd compression

Encrypt :
```
    import fernetfile.zstd

    with open(source, 'rb') as fin, fernetfile.zstd.open(destination, mode='wb', fernet_key=key) as fout:
        while True:
            data = fin.read(7777)
            if not data:
                break
            fout.write(data)
```

Decrypt :
```
    import fernetfile.zstd

    with fernetfile.zstd.open(source, mode='rb', fernet_key=key) as fin, open(destination, 'wb') as fout :
        while True:
            data = fin.read(8888)
            if not data:
                break
            fout.write(data)
```

## Use the fernet store

