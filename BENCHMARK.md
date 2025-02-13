# Benchmarks Coffer

Tests done with autoflush, with or without open_secure.

WT -1, ... are the last store.add time in store

WTime is the total write time (WT -1 + WT -2 + WT -3 + ...). RTime the time spent to read

| Class             | Data              | NbDocs | Op sec | Orig size | Crypt size | C Ratio | WTime  | Rtime  | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|TarZstdFernetFile  |genindex-all.html  |      5 | None   |      8776 |        324 |    3.70 |   0.14 |   0.03 |  0.02 |  0.03 |  0.02 |  0.02 |
|TarZstdFernetFile  |genindex-all.html  |      5 | zstd   |      8776 |        326 |    3.71 |   0.09 |   0.03 |  0.01 |  0.01 |  0.02 |  0.02 |
|TarZstdFernetFile  |genindex-all.html  |      5 | frnz   |      8776 |       1625 |   18.51 |   0.16 |   0.07 |  0.03 |  0.03 |  0.02 |  0.03 |
|TarZstdFernetFile  |genindex-all.html  |      5 | frnt   |      8776 |      11771 |  134.13 |   0.58 |   0.15 |  0.13 |  0.11 |  0.09 |  0.07 |
|TarZstdFernetFile  |genindex-all.html  |      5 | nacz   |      8776 |       1630 |   18.57 |   0.14 |   0.06 |  0.03 |  0.03 |  0.02 |  0.02 |
|TarZstdFernetFile  |genindex-all.html  |      5 | nacl   |      8776 |      11748 |  133.87 |   0.47 |   0.11 |  0.10 |  0.09 |  0.08 |  0.06 |
|TarZstdFernetFile  |genindex-all.html  |     20 | None   |     35103 |        328 |    0.93 |   0.52 |   0.12 |  0.03 |  0.03 |  0.03 |  0.03 |
|TarZstdFernetFile  |genindex-all.html  |     20 | zstd   |     35103 |        412 |    1.17 |   0.34 |   0.10 |  0.02 |  0.02 |  0.02 |  0.02 |
|TarZstdFernetFile  |genindex-all.html  |     20 | frnz   |     35103 |       6499 |   18.51 |   0.98 |   0.25 |  0.07 |  0.07 |  0.07 |  0.07 |
|TarZstdFernetFile  |genindex-all.html  |     20 | frnt   |     35103 |      47091 |  134.15 |  11.26 |   0.57 |  1.07 |  0.96 |  0.43 |  0.89 |
|TarZstdFernetFile  |genindex-all.html  |     20 | nacz   |     35103 |       6519 |   18.57 |   1.94 |   0.23 |  0.17 |  0.14 |  0.16 |  0.14 |
|TarZstdFernetFile  |genindex-all.html  |     20 | nacl   |     35103 |      46993 |  133.87 |  12.02 |   0.42 |  0.76 |  0.53 |  1.49 |  0.59 |
|TarZstdFernetFile  |searchindex.js     |      5 | None   |     19300 |       5908 |   30.61 |   0.94 |   0.12 |  0.23 |  0.19 |  0.14 |  0.06 |
|TarZstdFernetFile  |searchindex.js     |      5 | zstd   |     19300 |       1183 |    6.13 |   0.27 |   0.07 |  0.04 |  0.03 |  0.06 |  0.04 |
|TarZstdFernetFile  |searchindex.js     |      5 | frnz   |     19300 |       5927 |   30.71 |   0.58 |   0.14 |  0.14 |  0.07 |  0.09 |  0.06 |
|TarZstdFernetFile  |searchindex.js     |      5 | frnt   |     19300 |      25888 |  134.13 |   2.42 |   0.28 |  0.42 |  0.37 |  0.46 |  0.33 |
|TarZstdFernetFile  |searchindex.js     |      5 | nacz   |     19300 |       5921 |   30.68 |   1.28 |   0.12 |  0.32 |  0.22 |  0.10 |  0.27 |
|TarZstdFernetFile  |searchindex.js     |      5 | nacl   |     19300 |      25821 |  133.79 |   1.01 |   0.20 |  0.23 |  0.19 |  0.17 |  0.12 |
|TarZstdFernetFile  |searchindex.js     |     20 | None   |     77201 |      23636 |   30.62 |   6.74 |   0.48 |  0.58 |  0.55 |  0.52 |  0.49 |
|TarZstdFernetFile  |searchindex.js     |     20 | zstd   |     77201 |       1185 |    1.53 |   0.79 |   0.25 |  0.04 |  0.04 |  0.04 |  0.04 |
|TarZstdFernetFile  |searchindex.js     |     20 | frnz   |     77201 |      23707 |   30.71 |   2.89 |   0.55 |  0.22 |  0.21 |  0.20 |  0.23 |
|TarZstdFernetFile  |searchindex.js     |     20 | frnt   |     77201 |     103553 |  134.13 |  20.13 |   1.10 |  3.03 |  2.40 |  1.58 |  2.26 |
|TarZstdFernetFile  |searchindex.js     |     20 | nacz   |     77201 |      23683 |   30.68 |   2.59 |   0.45 |  0.18 |  0.18 |  0.17 |  0.16 |
|TarZstdFernetFile  |searchindex.js     |     20 | nacl   |     77201 |     103284 |  133.79 |  16.61 |   0.78 |  2.93 |  1.92 |  1.66 |  2.47 |
|TarZstdFernetFile  |using.pdf          |     10 | None   |     22170 |      28894 |  130.33 |   3.89 |   0.18 |  0.66 |  0.56 |  0.49 |  0.45 |
|TarZstdFernetFile  |using.pdf          |     10 | zstd   |     22170 |      28978 |  130.71 |   3.72 |   0.18 |  0.63 |  0.57 |  0.46 |  0.41 |
|TarZstdFernetFile  |using.pdf          |     10 | frnz   |     22170 |      29094 |  131.23 |   5.29 |   0.34 |  1.61 |  0.58 |  0.45 |  0.41 |
|TarZstdFernetFile  |using.pdf          |     10 | frnt   |     22170 |      29739 |  134.14 |   3.99 |   0.35 |  0.66 |  0.59 |  0.49 |  0.41 |
|TarZstdFernetFile  |using.pdf          |     10 | nacz   |     22170 |      29027 |  130.93 |   1.91 |   0.25 |  0.21 |  0.19 |  0.17 |  0.16 |
|TarZstdFernetFile  |using.pdf          |     10 | nacl   |     22170 |      29668 |  133.82 |   1.52 |   0.25 |  0.21 |  0.20 |  0.18 |  0.16 |
|TarZstdFernetFile  |using.pdf          |     50 | None   |    110849 |     144504 |  130.36 |  43.58 |   0.88 |  1.22 |  1.26 |  2.81 |  2.88 |
|TarZstdFernetFile  |using.pdf          |     50 | zstd   |    110849 |     144903 |  130.72 |  41.35 |   0.86 |  1.12 |  1.14 |  3.66 |  4.53 |
|TarZstdFernetFile  |using.pdf          |     50 | frnz   |    110849 |     145472 |  131.23 |  42.79 |   1.70 |  1.18 |  1.28 |  1.13 |  1.15 |
|TarZstdFernetFile  |using.pdf          |     50 | frnt   |    110849 |     148695 |  134.14 |  46.38 |   1.73 |  1.22 |  1.21 |  1.38 |  1.50 |
|TarZstdFernetFile  |using.pdf          |     50 | nacz   |    110849 |     145135 |  130.93 |  48.38 |   1.30 |  1.05 |  1.05 |  1.06 |  1.65 |
|TarZstdFernetFile  |using.pdf          |     50 | nacl   |    110849 |     148341 |  133.82 |  29.44 |   1.27 |  1.07 |  1.05 |  1.04 |  1.05 |
|TarZstdFernetFile  |library.pdf        |      5 | None   |     56690 |      73825 |  130.22 |   6.31 |   0.48 |  1.56 |  1.40 |  0.47 |  0.33 |
|TarZstdFernetFile  |library.pdf        |      5 | zstd   |     56690 |      73857 |  130.28 |   6.01 |   0.50 |  1.24 |  1.82 |  0.76 |  0.25 |
|TarZstdFernetFile  |library.pdf        |      5 | frnz   |     56690 |      74171 |  130.83 |   6.98 |   1.02 |  1.83 |  1.88 |  0.75 |  0.39 |
|TarZstdFernetFile  |library.pdf        |      5 | frnt   |     56690 |      76037 |  134.13 |   8.56 |   0.83 |  1.96 |  1.83 |  0.99 |  1.01 |
|TarZstdFernetFile  |library.pdf        |      5 | nacz   |     56690 |      73959 |  130.46 |   7.25 |   0.61 |  1.33 |  1.67 |  1.01 |  0.76 |
|TarZstdFernetFile  |library.pdf        |      5 | nacl   |     56690 |      75823 |  133.75 |   7.72 |   0.60 |  2.45 |  1.77 |  0.71 |  0.59 |
|TarZstdFernetFile  |library.pdf        |     20 | None   |    226762 |     295257 |  130.21 |  45.13 |   1.92 |  3.19 |  3.58 |  2.95 |  2.63 |
|TarZstdFernetFile  |library.pdf        |     20 | zstd   |    226762 |     295426 |  130.28 |  26.71 |   2.01 |  2.25 |  2.60 |  2.24 |  1.87 |
|TarZstdFernetFile  |library.pdf        |     20 | frnz   |    226762 |     296687 |  130.84 |  51.85 |   3.45 |  2.56 |  2.40 |  2.32 |  3.00 |
|TarZstdFernetFile  |library.pdf        |     20 | frnt   |    226762 |     304149 |  134.13 |  75.44 |   3.31 | 12.14 |  7.27 |  6.73 | 10.16 |
|TarZstdFernetFile  |library.pdf        |     20 | nacz   |    226762 |     295839 |  130.46 |  26.33 |   2.53 |  2.20 |  2.16 |  1.98 |  1.88 |
|TarZstdFernetFile  |library.pdf        |     20 | nacl   |    226762 |     303293 |  133.75 |  32.33 |   2.57 |  2.71 |  2.39 |  2.29 |  2.11 |
|TarZstdNaclFile    |genindex-all.html  |      5 | None   |      8776 |        243 |    2.77 |   0.11 |   0.03 |  0.02 |  0.02 |  0.02 |  0.01 |
|TarZstdNaclFile    |genindex-all.html  |      5 | zstd   |      8776 |        244 |    2.78 |   0.08 |   0.03 |  0.01 |  0.01 |  0.02 |  0.02 |
|TarZstdNaclFile    |genindex-all.html  |      5 | frnz   |      8776 |       1218 |   13.88 |   0.13 |   0.06 |  0.02 |  0.02 |  0.02 |  0.02 |
|TarZstdNaclFile    |genindex-all.html  |      5 | frnt   |      8776 |       8825 |  100.56 |   0.40 |   0.12 |  0.08 |  0.08 |  0.06 |  0.05 |
|TarZstdNaclFile    |genindex-all.html  |      5 | nacz   |      8776 |       1222 |   13.92 |   0.12 |   0.06 |  0.02 |  0.02 |  0.02 |  0.02 |
|TarZstdNaclFile    |genindex-all.html  |      5 | nacl   |      8776 |       8807 |  100.36 |   0.32 |   0.09 |  0.08 |  0.07 |  0.04 |  0.04 |
|TarZstdNaclFile    |genindex-all.html  |     20 | None   |     35103 |        246 |    0.70 |   0.48 |   0.14 |  0.03 |  0.03 |  0.03 |  0.03 |
|TarZstdNaclFile    |genindex-all.html  |     20 | zstd   |     35103 |        245 |    0.70 |   0.32 |   0.10 |  0.02 |  0.02 |  0.02 |  0.02 |
|TarZstdNaclFile    |genindex-all.html  |     20 | frnz   |     35103 |       4872 |   13.88 |   0.94 |   0.26 |  0.07 |  0.08 |  0.09 |  0.09 |
|TarZstdNaclFile    |genindex-all.html  |     20 | frnt   |     35103 |      35304 |  100.57 |   3.40 |   0.46 |  0.28 |  0.26 |  0.23 |  0.22 |
|TarZstdNaclFile    |genindex-all.html  |     20 | nacz   |     35103 |       4887 |   13.92 |   0.66 |   0.21 |  0.05 |  0.04 |  0.04 |  0.04 |
|TarZstdNaclFile    |genindex-all.html  |     20 | nacl   |     35103 |      35229 |  100.36 |   2.40 |   0.31 |  0.19 |  0.18 |  0.17 |  0.16 |
|TarZstdNaclFile    |searchindex.js     |      5 | None   |     19300 |       4430 |   22.95 |   0.53 |   0.09 |  0.13 |  0.10 |  0.08 |  0.06 |
|TarZstdNaclFile    |searchindex.js     |      5 | zstd   |     19300 |        887 |    4.59 |   0.16 |   0.06 |  0.03 |  0.03 |  0.03 |  0.03 |
|TarZstdNaclFile    |searchindex.js     |      5 | frnz   |     19300 |       4443 |   23.02 |   0.30 |   0.12 |  0.06 |  0.06 |  0.05 |  0.05 |
|TarZstdNaclFile    |searchindex.js     |      5 | frnt   |     19300 |      19409 |  100.56 |   0.95 |   0.23 |  0.21 |  0.18 |  0.16 |  0.13 |
|TarZstdNaclFile    |searchindex.js     |      5 | nacz   |     19300 |       4439 |   23.00 |   0.28 |   0.10 |  0.07 |  0.06 |  0.05 |  0.04 |
|TarZstdNaclFile    |searchindex.js     |      5 | nacl   |     19300 |      19357 |  100.29 |   0.69 |   0.15 |  0.14 |  0.13 |  0.11 |  0.09 |
|TarZstdNaclFile    |searchindex.js     |     20 | None   |     77201 |      17719 |   22.95 |   5.76 |   0.39 |  0.49 |  0.46 |  0.45 |  0.42 |
|TarZstdNaclFile    |searchindex.js     |     20 | zstd   |     77201 |        888 |    1.15 |   0.69 |   0.24 |  0.04 |  0.04 |  0.04 |  0.04 |
|TarZstdNaclFile    |searchindex.js     |     20 | frnz   |     77201 |      17773 |   23.02 |   2.06 |   0.48 |  0.16 |  0.15 |  0.14 |  0.13 |
|TarZstdNaclFile    |searchindex.js     |     20 | frnt   |     77201 |      77634 |  100.56 |  16.63 |   0.89 |  3.34 |  3.40 |  2.23 |  0.55 |
|TarZstdNaclFile    |searchindex.js     |     20 | nacz   |     77201 |      17754 |   23.00 |   3.94 |   0.41 |  0.13 |  0.40 |  0.36 |  0.34 |
|TarZstdNaclFile    |searchindex.js     |     20 | nacl   |     77201 |      77428 |  100.29 |  14.37 |   0.65 |  1.52 |  1.26 |  1.45 |  1.23 |
|TarZstdNaclFile    |using.pdf          |     10 | None   |     22170 |      21662 |   97.71 |   2.60 |   0.15 |  0.19 |  0.57 |  0.34 |  0.35 |
|TarZstdNaclFile    |using.pdf          |     10 | zstd   |     22170 |      21724 |   97.99 |   0.98 |   0.11 |  0.14 |  0.13 |  0.13 |  0.10 |
|TarZstdNaclFile    |using.pdf          |     10 | frnz   |     22170 |      21812 |   98.38 |   1.25 |   0.29 |  0.16 |  0.15 |  0.14 |  0.13 |
|TarZstdNaclFile    |using.pdf          |     10 | frnt   |     22170 |      22295 |  100.56 |   1.32 |   0.28 |  0.19 |  0.16 |  0.15 |  0.14 |
|TarZstdNaclFile    |using.pdf          |     10 | nacz   |     22170 |      21760 |   98.15 |   0.93 |   0.19 |  0.13 |  0.12 |  0.10 |  0.10 |
|TarZstdNaclFile    |using.pdf          |     10 | nacl   |     22170 |      22241 |  100.32 |   1.63 |   0.18 |  0.37 |  0.19 |  0.11 |  0.10 |
|TarZstdNaclFile    |using.pdf          |     50 | None   |    110849 |     108333 |   97.73 |  52.99 |   0.58 |  0.82 |  0.77 |  2.91 |  1.64 |
|TarZstdNaclFile    |using.pdf          |     50 | zstd   |    110849 |     108629 |   98.00 |  20.07 |   0.55 |  0.76 |  0.73 |  0.72 |  0.70 |
|TarZstdNaclFile    |using.pdf          |     50 | frnz   |    110849 |     109061 |   98.39 |  36.95 |   1.41 |  3.11 |  1.49 |  0.73 |  0.73 |
|TarZstdNaclFile    |using.pdf          |     50 | frnt   |    110849 |     111478 |  100.57 |  37.05 |   1.40 |  0.80 |  0.77 |  0.76 |  0.73 |
|TarZstdNaclFile    |using.pdf          |     50 | nacz   |    110849 |     108802 |   98.15 |  27.04 |   0.95 |  2.12 |  2.25 |  2.67 |  1.97 |
|TarZstdNaclFile    |using.pdf          |     50 | nacl   |    110849 |     111205 |  100.32 |  28.29 |   0.92 |  0.65 |  0.58 |  0.61 |  0.61 |
|TarZstdNaclFile    |library.pdf        |      5 | None   |     56690 |      55348 |   97.63 |   2.31 |   0.34 |  0.57 |  0.48 |  0.35 |  0.24 |
|TarZstdNaclFile    |library.pdf        |      5 | zstd   |     56690 |      55368 |   97.67 |   1.48 |   0.34 |  0.34 |  0.28 |  0.23 |  0.17 |
|TarZstdNaclFile    |library.pdf        |      5 | frnz   |     56690 |      55606 |   98.09 |   2.23 |   0.66 |  0.52 |  0.43 |  0.37 |  0.29 |
|TarZstdNaclFile    |library.pdf        |      5 | frnt   |     56690 |      57006 |  100.56 |   4.11 |   0.64 |  0.83 |  0.87 |  0.79 |  0.64 |
|TarZstdNaclFile    |library.pdf        |      5 | nacz   |     56690 |      55444 |   97.80 |   1.69 |   0.43 |  0.39 |  0.33 |  0.26 |  0.22 |
|TarZstdNaclFile    |library.pdf        |      5 | nacl   |     56690 |      56842 |  100.27 |   2.72 |   0.49 |  0.60 |  0.53 |  0.46 |  0.43 |
|TarZstdNaclFile    |library.pdf        |     20 | None   |    226762 |     221362 |   97.62 |  44.60 |   1.30 |  2.22 |  2.08 |  2.52 |  5.28 |
|TarZstdNaclFile    |library.pdf        |     20 | zstd   |    226762 |     221469 |   97.67 |  40.46 |   1.30 |  4.80 |  4.29 |  2.46 |  1.13 |
|TarZstdNaclFile    |library.pdf        |     20 | frnz   |    226762 |     222427 |   98.09 |  33.82 |   2.68 |  4.08 |  1.54 |  1.48 |  1.39 |
|TarZstdNaclFile    |library.pdf        |     20 | frnt   |    226762 |     228022 |  100.56 |  37.38 |   3.10 |  2.17 |  2.09 |  2.05 |  1.95 |
|TarZstdNaclFile    |library.pdf        |     20 | nacz   |    226762 |     221779 |   97.80 |  34.35 |   2.17 |  1.53 |  4.07 |  4.52 |  3.40 |
|TarZstdNaclFile    |library.pdf        |     20 | nacl   |    226762 |     227367 |  100.27 |  40.51 |   1.73 |  6.96 |  1.79 |  2.09 |  1.82 |
