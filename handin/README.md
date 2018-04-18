# Apriori
How to run:
* `python3 apriori.py [-h] [--factors FACTORS] [--rules] [--plot] data_file min_supp min_conf name_file`
* if you specify the `--factors` flag, supply the transcription factors file right after. Supply the genes file as the name_file.
* -h shows a usage message
* data\_file is the file with all of the baskets
* min_supp and min_conf are self explanatory
* name\_file is the file with all of the names of basket items
* the --plot flag plots various minimum supports and confidences, but it may require tweaking the code to run quickly.
