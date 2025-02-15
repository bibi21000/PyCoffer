# Benchmarks Coffer

Tests done with autoflush, with or without open_secure.

WT -1, ... are the last store.add time in store

WTime is the total write time (WT -1 + WT -2 + WT -3 + ...). RTime the time spent to read

| Class             | Data              | NbDocs | Orig size | Crypt size | C Ratio | WTime  | Rtime  | WT -1 | WT -2 | WT -3 | WT -4 |
|:------------------|:------------------|-------:|----------:|-----------:|--------:|-------:|-------:|------:|------:|------:|------:|
|CofferBank         |genindex-all.html  |      5 |      8776 |       1630 |   18.57 |   0.16 |   0.06 |  0.03 |  0.03 |  0.02 |  0.02 |
|CofferStore        |genindex-all.html  |      5 |      8776 |        189 |    2.15 |   0.34 |   0.02 |  0.06 |  0.07 |  0.06 |  0.06 |
|CofferMarket       |genindex-all.html  |      5 |      8776 |        942 |   10.74 |   0.38 |   0.05 |  0.07 |  0.07 |  0.07 |  0.07 |
|CofferBank         |searchindex.js     |      5 |     19300 |       5921 |   30.68 |   0.34 |   0.11 |  0.07 |  0.06 |  0.06 |  0.05 |
|CofferStore        |searchindex.js     |      5 |     19300 |        705 |    3.65 |   0.96 |   0.07 |  0.19 |  0.19 |  0.19 |  0.19 |
|CofferMarket       |searchindex.js     |      5 |     19300 |       3522 |   18.25 |   1.03 |   0.10 |  0.20 |  0.20 |  0.19 |  0.19 |
|CofferBank         |library.pdf        |      5 |     56690 |      73959 |  130.46 |   2.64 |   0.50 |  0.64 |  0.52 |  0.43 |  0.33 |
|CofferStore        |library.pdf        |      5 |     56690 |      54937 |   96.91 |   3.56 |   0.25 |  0.43 |  0.63 |  0.65 |  0.77 |
|CofferMarket       |library.pdf        |      5 |     56690 |      54936 |   96.91 |   2.68 |   0.28 |  0.46 |  0.45 |  0.50 |  0.53 |
|CofferBank         |mixed              |      5 |     95906 |      96041 |  100.14 |  19.59 |   0.78 |  3.06 |  7.23 |  4.93 |  2.99 |
|CofferStore        |mixed              |      5 |     95906 |      68459 |   71.38 |   4.50 |   0.45 |  0.92 |  0.83 |  0.85 |  0.80 |
|CofferMarket       |mixed              |      5 |     95906 |      70248 |   73.25 |   5.02 |   0.58 |  1.00 |  0.82 |  0.81 |  0.94 |
|CofferBank         |genindex-all.html  |     25 |     43879 |       8149 |   18.57 |   2.34 |   0.26 |  0.18 |  0.18 |  0.21 |  0.24 |
|CofferStore        |genindex-all.html  |     25 |     43879 |        189 |    0.43 |   1.60 |   0.09 |  0.06 |  0.06 |  0.06 |  0.06 |
|CofferMarket       |genindex-all.html  |     25 |     43879 |       4712 |   10.74 |   1.81 |   0.21 |  0.07 |  0.07 |  0.07 |  0.07 |
|CofferBank         |searchindex.js     |     25 |     96501 |      29604 |   30.68 |   8.99 |   0.51 |  0.62 |  0.61 |  0.60 |  0.55 |
|CofferStore        |searchindex.js     |     25 |     96501 |        706 |    0.73 |   4.63 |   0.25 |  0.19 |  0.18 |  0.19 |  0.19 |
|CofferMarket       |searchindex.js     |     25 |     96501 |      17613 |   18.25 |   4.96 |   0.38 |  0.19 |  0.19 |  0.19 |  0.19 |
|CofferBank         |library.pdf        |     25 |    283452 |     369799 |  130.46 |  90.02 |   2.49 |  6.72 |  3.79 |  2.74 |  7.17 |
|CofferStore        |library.pdf        |     25 |    283452 |     274683 |   96.91 |  12.25 |   1.31 |  0.50 |  0.43 |  0.42 |  0.44 |
|CofferMarket       |library.pdf        |     25 |    283452 |     274681 |   96.91 |  13.37 |   1.27 |  0.45 |  0.44 |  0.45 |  0.46 |
|CofferBank         |mixed              |     25 |    479529 |     480174 |  100.13 | 427.48 |   3.92 | 36.34 | 46.47 | 29.72 | 14.61 |
|CofferStore        |mixed              |     25 |    479529 |     343226 |   71.58 |  21.25 |   1.76 |  1.17 |  0.76 |  0.75 |  0.76 |
|CofferMarket       |mixed              |     25 |    479529 |     351234 |   73.25 |  21.74 |   2.37 |  0.82 |  0.81 |  0.83 |  0.80 |
