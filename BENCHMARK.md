# Benchmarks Coffer

Tests done with autoflush, with or without open_secure.

WT -1, ... are the last store.add time in store

WTime is the total write time (WT -1 + WT -2 + WT -3 + ...).

Extime the time spent to extract all files from coffer

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|CofferBank         |genindex-all.html  |      5 |      8776 |       1221 |   13.92 |   0.35 |   0.08 |  0.04 |  0.03 |  0.03 |  0.03 |
|CofferStore        |genindex-all.html  |      5 |      8776 |        189 |    2.15 |   0.34 |   0.03 |  0.06 |  0.06 |  0.07 |  0.06 |
|CofferMarket       |genindex-all.html  |      5 |      8776 |        942 |   10.74 |   0.40 |   0.06 |  0.07 |  0.07 |  0.07 |  0.07 |
|CofferBank         |searchindex.js     |      5 |     19300 |       4438 |   22.99 |   0.39 |   0.14 |  0.09 |  0.07 |  0.06 |  0.06 |
|CofferStore        |searchindex.js     |      5 |     19300 |        705 |    3.65 |   0.96 |   0.06 |  0.19 |  0.19 |  0.19 |  0.18 |
|CofferMarket       |searchindex.js     |      5 |     19300 |       3522 |   18.25 |   1.03 |   0.10 |  0.19 |  0.20 |  0.20 |  0.19 |
|CofferBank         |library.pdf        |      5 |     56690 |      55435 |   97.79 |   2.68 |   0.65 |  0.62 |  0.52 |  0.45 |  0.33 |
|CofferStore        |library.pdf        |      5 |     56690 |      54937 |   96.91 |   2.55 |   0.35 |  0.46 |  0.45 |  0.45 |  0.44 |
|CofferMarket       |library.pdf        |      5 |     56690 |      54936 |   96.91 |   2.65 |   0.31 |  0.48 |  0.47 |  0.47 |  0.47 |
|CofferBank         |mixed              |      5 |     95906 |      71986 |   75.06 |   9.94 |   1.05 |  3.21 |  2.53 |  1.84 |  1.12 |
|CofferStore        |mixed              |      5 |     95906 |      68459 |   71.38 |   4.17 |   0.39 |  0.77 |  0.77 |  0.77 |  0.77 |
|CofferMarket       |mixed              |      5 |     95906 |      70248 |   73.25 |   4.58 |   0.60 |  0.83 |  0.83 |  0.84 |  0.84 |
|CofferBank         |genindex-all.html  |     25 |     43879 |       6108 |   13.92 |   1.47 |   0.38 |  0.09 |  0.08 |  0.08 |  0.08 |
|CofferStore        |genindex-all.html  |     25 |     43879 |        189 |    0.43 |   1.65 |   0.11 |  0.06 |  0.06 |  0.06 |  0.06 |
|CofferMarket       |genindex-all.html  |     25 |     43879 |       4712 |   10.74 |   1.90 |   0.33 |  0.07 |  0.07 |  0.07 |  0.07 |
|CofferBank         |searchindex.js     |     25 |     96501 |      22189 |   22.99 |   3.98 |   0.69 |  0.24 |  0.23 |  0.23 |  0.23 |
|CofferStore        |searchindex.js     |     25 |     96501 |        706 |    0.73 |   4.85 |   0.25 |  0.18 |  0.18 |  0.18 |  0.18 |
|CofferMarket       |searchindex.js     |     25 |     96501 |      17613 |   18.25 |   5.09 |   0.49 |  0.20 |  0.20 |  0.20 |  0.20 |
|CofferBank         |library.pdf        |     25 |    283452 |     277176 |   97.79 |  67.14 |   3.15 |  7.29 |  6.32 |  6.04 |  6.57 |
|CofferStore        |library.pdf        |     25 |    283452 |     274683 |   96.91 |  11.89 |   1.27 |  0.42 |  0.42 |  0.42 |  0.42 |
|CofferMarket       |library.pdf        |     25 |    283452 |     274681 |   96.91 |  13.02 |   1.49 |  0.47 |  0.46 |  0.47 |  0.45 |
|CofferBank         |mixed              |     25 |    479529 |     359907 |   75.05 | 376.83 |   5.49 | 34.70 | 31.81 | 24.67 | 35.77 |
|CofferStore        |mixed              |     25 |    479529 |     343226 |   71.58 |  20.94 |   1.89 |  0.76 |  0.73 |  0.78 |  0.74 |
|CofferMarket       |mixed              |     25 |    479529 |     351234 |   73.25 |  22.38 |   3.19 |  0.82 |  0.83 |  0.81 |  0.92 |


# Benchmarks Coffer with cache in tmpfs

mount -t tmpfs tmpfs /tmp/coffertmp/ -o size=4g

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|CofferBank         |mixed              |     25 |    479529 |     359906 |   75.05 | 407.81 |   5.23 | 35.90 | 16.82 | 24.39 | 36.31 |
|CofferStore        |mixed              |     25 |    479529 |     351235 |   73.25 |  20.84 |   1.80 |  0.76 |  0.76 |  0.77 |  0.78 |
|CofferMarket       |mixed              |     25 |    479529 |     351233 |   73.25 |  22.80 |   2.89 |  0.83 |  0.83 |  0.82 |  0.82 |
