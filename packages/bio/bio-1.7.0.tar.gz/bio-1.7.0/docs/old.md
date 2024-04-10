to fetch the data from NCBI and rename data to more meaningful labels, then write:

    bio align ncov:S ratg13:S --end 60 --pep1

to align the DNA for the S protein while also showing the translation with one letter peptide code:

```
# Ident=57(95.0%)  Mis=3(5.0%)  Gaps=0(0.0%)  Target=(1, 60)  Query=(1, 60)  Length=60  Score=273.0  NUC.4.4(11,1)

              M  F  V  F  L  V  L  L  P  L  V  S  S  Q  C  V  N  L  T  T
YP_009724390 ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTCTCTAGTCAGTGTGTTAATCTTACAACC
             ||||||||||||||||||||||||||||||||.||||||||||||||||||||.|||||. 60
QHR63300.2   ATGTTTGTTTTTCTTGTTTTATTGCCACTAGTTTCTAGTCAGTGTGTTAATCTAACAACT
              M  F  V  F  L  V  L  L  P  L  V  S  S  Q  C  V  N  L  T  T
```

`bio` was designed to use words that make sense: align, translate, complement, protein, taxon, type, etc. If you wanted to align the same sequences when translated into proteins `bio` lets you write:

    bio align ncov:S ratg13:S --end 60 --translate

to generate:

```
# Ident=20(100.0%)  Mis=0(0.0%)  Gaps=0(0.0%)  Target=(1, 20)  Query=(1, 20)  Length=20  Score=98.0  BLOSUM62(11,1)

YP_009724390 MFVFLVLLPLVSSQCVNLTT
             |||||||||||||||||||| 20
QHR63300.2   MFVFLVLLPLVSSQCVNLTT
```

Beyond alignments, there is a lot more to `bio`. We recommend looking at the [documentation][docs]
