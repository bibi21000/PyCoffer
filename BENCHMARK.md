# Benchmarks Coffer

Tests done with autoflush, with or without open_secure.

WT -1, ... are the last store.add time in store

WTime is the total write time (WT -1 + WT -2 + WT -3 + ...).

Extime the time spent to extract all files from coffer

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|CofferBank         |genindex-all.html  |      5 |      8776 |       1221 |   13.92 |   0.36 |   0.09 |  0.04 |  0.03 |  0.03 |  0.03 |
|CofferStore        |genindex-all.html  |      5 |      8776 |        188 |    2.15 |   0.36 |   0.03 |  0.07 |  0.07 |  0.07 |  0.07 |
|CofferMarket       |genindex-all.html  |      5 |      8776 |        942 |   10.74 |   0.47 |   0.08 |  0.10 |  0.08 |  0.08 |  0.08 |
|CofferBank         |searchindex.js     |      5 |     19300 |       4438 |   22.99 |   0.48 |   0.15 |  0.08 |  0.07 |  0.07 |  0.10 |
|CofferStore        |searchindex.js     |      5 |     19300 |        705 |    3.65 |   0.99 |   0.06 |  0.20 |  0.19 |  0.19 |  0.19 |
|CofferMarket       |searchindex.js     |      5 |     19300 |       3522 |   18.25 |   1.09 |   0.12 |  0.22 |  0.20 |  0.20 |  0.21 |
|CofferBank         |library.pdf        |      5 |     56690 |      55435 |   97.79 |   2.72 |   0.64 |  0.66 |  0.52 |  0.43 |  0.32 |
|CofferStore        |library.pdf        |      5 |     56690 |      54937 |   96.91 |   2.47 |   0.28 |  0.45 |  0.44 |  0.45 |  0.44 |
|CofferMarket       |library.pdf        |      5 |     56690 |      54936 |   96.91 |   2.68 |   0.30 |  0.47 |  0.47 |  0.48 |  0.47 |
|CofferBank         |mixed              |      5 |     95906 |      71986 |   75.06 |   9.69 |   1.05 |  3.16 |  2.45 |  1.76 |  1.11 |
|CofferStore        |mixed              |      5 |     95906 |      68459 |   71.38 |   4.30 |   0.41 |  0.80 |  0.77 |  0.79 |  0.77 |
|CofferMarket       |mixed              |      5 |     95906 |      70248 |   73.25 |   4.87 |   0.61 |  0.84 |  1.05 |  0.88 |  0.85 |
|CofferBank         |genindex-all.html  |     25 |     43879 |       6108 |   13.92 |   1.48 |   0.39 |  0.09 |  0.08 |  0.08 |  0.08 |
|CofferStore        |genindex-all.html  |     25 |     43879 |        189 |    0.43 |   1.70 |   0.11 |  0.06 |  0.07 |  0.06 |  0.06 |
|CofferMarket       |genindex-all.html  |     25 |     43879 |       4712 |   10.74 |   1.99 |   0.33 |  0.08 |  0.08 |  0.08 |  0.08 |
|CofferBank         |searchindex.js     |     25 |     96501 |      22189 |   22.99 |   3.88 |   0.69 |  0.24 |  0.23 |  0.23 |  0.22 |
|CofferStore        |searchindex.js     |     25 |     96501 |        706 |    0.73 |   4.68 |   0.26 |  0.18 |  0.18 |  0.19 |  0.18 |
|CofferMarket       |searchindex.js     |     25 |     96501 |      17613 |   18.25 |   5.06 |   0.49 |  0.20 |  0.19 |  0.20 |  0.20 |
|CofferBank         |library.pdf        |     25 |    283452 |     277176 |   97.79 |  40.18 |   3.27 |  2.84 |  2.62 |  2.34 |  2.40 |
|CofferStore        |library.pdf        |     25 |    283452 |     274683 |   96.91 |  12.15 |   1.31 |  0.44 |  0.44 |  0.45 |  0.44 |
|CofferMarket       |library.pdf        |     25 |    283452 |     274681 |   96.91 |  13.64 |   1.53 |  0.49 |  0.49 |  0.49 |  0.48 |
|CofferBank         |mixed              |     25 |    479529 |     359906 |   75.05 | 223.19 |   5.37 | 17.22 | 16.26 | 15.87 | 15.20 |
|CofferStore        |mixed              |     25 |    479529 |     343226 |   71.58 |  20.39 |   1.92 |  0.76 |  0.76 |  0.83 |  0.75 |
|CofferMarket       |mixed              |     25 |    479529 |     351234 |   73.25 |  22.63 |   3.12 |  0.84 |  0.83 |  0.84 |  1.04 |
# Benchmarks Coffer with cache in tmpfs

mount -t tmpfs tmpfs /tmp/coffertmp/ -o size=4g

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
