# Benchmarks Coffer

Tests done with autoflush, with or without open_secure.

WT -1, ... are the last store.add time in store

WTime is the total write time (WT -1 + WT -2 + WT -3 + ...).

Extime the time spent to extract all files from coffer

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|CofferBank         |genindex-all.html  |      5 |      8776 |       1630 |   18.57 |   0.19 |   0.08 |  0.04 |  0.03 |  0.03 |  0.03 |
|CofferStore        |genindex-all.html  |      5 |      8776 |        189 |    2.15 |   0.34 |   0.03 |  0.06 |  0.07 |  0.06 |  0.07 |
|CofferMarket       |genindex-all.html  |      5 |      8776 |        942 |   10.74 |   0.41 |   0.07 |  0.08 |  0.07 |  0.07 |  0.07 |
|CofferBank         |searchindex.js     |      5 |     19300 |       5921 |   30.68 |   0.38 |   0.14 |  0.08 |  0.07 |  0.06 |  0.06 |
|CofferStore        |searchindex.js     |      5 |     19300 |        705 |    3.65 |   0.95 |   0.08 |  0.19 |  0.18 |  0.19 |  0.18 |
|CofferMarket       |searchindex.js     |      5 |     19300 |       3522 |   18.25 |   1.05 |   0.12 |  0.20 |  0.20 |  0.19 |  0.20 |
|CofferBank         |library.pdf        |      5 |     56690 |      73959 |  130.46 |   2.78 |   0.59 |  0.67 |  0.55 |  0.44 |  0.34 |
|CofferStore        |library.pdf        |      5 |     56690 |      54937 |   96.91 |   2.46 |   0.27 |  0.44 |  0.45 |  0.44 |  0.44 |
|CofferMarket       |library.pdf        |      5 |     56690 |      54936 |   96.91 |   2.70 |   0.30 |  0.48 |  0.49 |  0.48 |  0.48 |
|CofferBank         |mixed              |      5 |     95906 |      96041 |  100.14 |  20.43 |   0.98 |  9.30 |  5.40 |  1.87 |  1.15 |
|CofferStore        |mixed              |      5 |     95906 |      68459 |   71.38 |   4.14 |   0.39 |  0.76 |  0.75 |  0.75 |  0.77 |
|CofferMarket       |mixed              |      5 |     95906 |      70248 |   73.25 |   4.48 |   0.60 |  0.83 |  0.82 |  0.82 |  0.82 |
|CofferBank         |genindex-all.html  |     25 |     43879 |       8149 |   18.57 |   1.51 |   0.37 |  0.09 |  0.09 |  0.08 |  0.08 |
|CofferStore        |genindex-all.html  |     25 |     43879 |        189 |    0.43 |   1.58 |   0.10 |  0.06 |  0.06 |  0.07 |  0.06 |
|CofferMarket       |genindex-all.html  |     25 |     43879 |       4712 |   10.74 |   1.83 |   0.31 |  0.07 |  0.07 |  0.07 |  0.07 |
|CofferBank         |searchindex.js     |     25 |     96501 |      29604 |   30.68 |   3.96 |   0.63 |  0.26 |  0.25 |  0.25 |  0.23 |
|CofferStore        |searchindex.js     |     25 |     96501 |        706 |    0.73 |   4.68 |   0.25 |  0.18 |  0.19 |  0.18 |  0.18 |
|CofferMarket       |searchindex.js     |     25 |     96501 |      17613 |   18.25 |   4.88 |   0.48 |  0.19 |  0.19 |  0.19 |  0.19 |
|CofferBank         |library.pdf        |     25 |    283452 |     369799 |  130.46 |  70.12 |   2.86 |  2.82 |  4.45 |  7.99 |  6.12 |
|CofferStore        |library.pdf        |     25 |    283452 |     274683 |   96.91 |  11.62 |   1.27 |  0.41 |  0.42 |  0.42 |  0.42 |
|CofferMarket       |library.pdf        |     25 |    283452 |     274681 |   96.91 |  12.73 |   1.48 |  0.45 |  0.50 |  0.46 |  0.45 |
|CofferBank         |mixed              |     25 |    479529 |     480174 |  100.13 | 425.42 |   4.88 | 37.28 | 28.07 | 37.03 | 25.34 |
|CofferStore        |mixed              |     25 |    479529 |     343226 |   71.58 |  19.95 |   1.88 |  0.75 |  0.75 |  0.80 |  0.78 |
|CofferMarket       |mixed              |     25 |    479529 |     351234 |   73.25 |  21.83 |   3.08 |  0.81 |  0.81 |  0.80 |  0.81 |


# Benchmarks Coffer with cache in tmpfs

mount -t tmpfs tmpfs /tmp/coffertmp/ -o size=4g

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Extime | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|CofferBank         |mixed              |     25 |    479529 |     480173 |  100.13 | 426.17 |   4.84 | 28.87 | 37.77 | 32.56 | 32.01 |
|CofferStore        |mixed              |     25 |    479529 |     351233 |   73.25 |  19.97 |   1.84 |  0.71 |  0.72 |  0.72 |  0.73 |
|CofferMarket       |mixed              |     25 |    479529 |     351233 |   73.25 |  21.80 |   2.92 |  0.80 |  0.80 |  0.80 |  0.81 |
