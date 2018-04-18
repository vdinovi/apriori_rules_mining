# Team
Vittorio Dinovi (vdinovi)
BillyGottenstrater (BillyGottenstrater)

* For the Bakery dataset, our program takes <size>-out1.csv and goods.csv
* For the Bingo dataset, our program takes bingoBaskets.csv and authlist.psv
* For the Transcription dataset, our program takes factor_baskets_sparse.csv, genes.csv and factors.csv (see the note on running transcriptions)



# Apriori Program
The program produces a freq_isets.txt file containing discovered skyline frequent item sets and their corresponding supports. 
If --rules is specified, a rules.txt id produced file containing the discovered skyline rules and their corresponding confidences.
Finally if --plot is specified, the program generates a plot of supports x freq isets discovered and a plot of confidences x rules discovered. Note that there are hardcoded ranges, decrement amounts, so this option should not be specified unless these values are correct for the given dataset. This generates the files 'support.png', 'support.txt', 'confidence.png', and 'confidence.txt'.

Note: for the transcription dataset, since their are 2 name files, run with the flag and factors filename `--factors factors.csv` and genes file as the regular name_file. Trying to analyze transcriptions otherwise will not work.
ex) python apriori.py --factors factors.csv factor_baskets_sparse.csv 0.5 0.5 genes.csv

How to run:
* `python3 apriori.py [-h] [--factors FACTORS] [--rules] [--plot] data_file min_supp min_conf name_file`
* if you specify the `--factors` flag, supply the transcription factors file right after.
* -h shows a usage message
* data\_file is the file with all of the baskets
* name\_file is the file with all of the names of basket items

r
