import csv, pdb, itertools
from pprint import pprint
import matplotlib.pyplot as plt
import math
import re


def parse_data_file(filename):
    baskets = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            baskets[int(row[0])] = set(map(lambda x: int(x), row[1:]))
    return baskets

def parse_t(data_file, gene_file, factors_file):
   baskets = {}
   genes = {}
   factors = {}
   with open(data_file, 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
         gene = int(row.pop('expgene'))
         factorlist = row.pop(None)
         allfactors = []
         for i in range(0,len(factorlist)-1,2):
             allfactors.append(i)
         baskets[gene] = set(allfactors)
   with open(factors_file, 'r') as file:
      reader = csv.DictReader(file)
      for row in reader:
         key = int(row.pop('tf_id'))
         factors[key] = row
   return baskets,genes, factors

def parse_transcription_files(data_filename, gene_file, factors_file):
    baskets = {}
    genes = {}
    factors = {}
    with open(data_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            gene = int(row.pop('expgene'))
            factor = int(row.pop('tf_id'))
            baskets[gene] = {gene, factor}
    with open(gene_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            id = int(row.pop('expgene'))
            genes[id] = ",".join([row.pop('geneabbrev'), row.pop('experiment'), row.pop('species')])
    with open(factors_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            id = int(row.pop('tf_id'))
            factors[id] = row.pop('transfac')
    return baskets, genes, factors


def parse_name_file(filename):
    result = {}
    if re.match(".*\.csv", filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = int(row.pop('Id'))
                for k, v in row.items():
                    row[k] = v.replace("'", "")
                result[key] = row
        return result
    elif re.match(".*\.psv", filename):
        with open(filename, 'r') as file:
            for row in file.readlines():
                line = row.split('|')
                result[int(line[0].lstrip().rstrip())] = line[1].lstrip().rstrip()
        return result
    else:
        print("filetype '{}' not recognized".format(filename))
        exit()

def support(T, item_set, supports):
    count = 0
    iset = frozenset(item_set)
    if iset in supports:
        return supports[iset]
    for _, basket in T.items():
        if item_set.issubset(basket):
            count += 1 
    supports[iset] = (1.0 * count) / len(T)
    return supports[iset]

def confidence(T, a, b, supports):
    return support(T, a.union(b), supports) / support(T, a, supports)

# From itertools recipe "pairwise"
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

# From itertools recipe "powerset"
def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))


def candidates_gen(F, k):
    candidates = []
    for f1 in F:
        f1_len = len(f1)
        if f1_len != k:
            continue
        for f2 in F:
            f2_len = len(f2)
            if f1_len != f2_len:
                continue
            c = f1 | f2
            if len(c) == f1_len + 1:
                flag = True
                for s in powerset(c):
                    if len(s) == len(c) - 1 and (set(s) not in F):
                        flag = False
                if flag:
                    candidates.append(c)
    return set(candidates)

def apriori(T, I, min_sup, supports):
    freq_sets = [[], [frozenset({i}) for i in I if support(T, {i}, supports) >= min_sup]]
    k = 2
    while freq_sets[k-1]:
        candidates = candidates_gen(freq_sets[k-1], k-1)
        counts = {c: 0 for c in candidates}
        for _, basket in T.items():
            for c in (c for c in candidates if c.issubset(basket)):
                counts[c] += 1
        g = [c for c in candidates if ((1.0 * counts[c]/len(T)) >= min_sup)]
        freq_sets.append(g)
        k += 1
    return [set(f) for fs in freq_sets for f in fs]

def get_skyline(F):
    items = {frozenset(s) for s in F}
    skyline = []
    for f in F:
        flag = True
        for f1 in F:
            if f != f1 and f.issubset(f1):
                flag = False
                break
        if flag:
            skyline.append(f)
    return skyline

def gen_rules(F, T, min_conf, supports):
    rules = []
    for f in (f for f in F if len(f) >= 2):
        base = []
        for b in f:
            a = f - {b}
            if confidence(T, a, {b}, supports) >= min_conf:
                base.append((a, {b}))
        rules += base
    return rules

def plot_supp(plot_filename, text_filename, dataset, start_supp, end_supp):
    dx = 0.002
    supp = start_supp
    items = frozenset(dataset.keys())
    min_supports = []
    isets_found = []
    supports = {}
    with open(text_filename, 'w') as file:
        while True:
            freq_isets = get_skyline(apriori(dataset, items, supp, supports))
            min_supports.append(supp)
            isets_found.append(len(freq_isets))
            file.write("{:08f} -> {}\n".format(supp, len(freq_isets)))
            print("  {:08f} -> {}".format(supp, len(freq_isets)))
            supp -= dx
            if supp - dx < end_supp:
                break
    plt.clf()
    plt.plot(min_supports, isets_found)
    plt.xlabel("minimum support value")
    plt.ylabel("freq item sets found")
    plt.savefig(plot_filename)


def plot_conf(plot_filename, text_filename, dataset, supp, start_conf, end_conf):
    dx = 0.005
    items = frozenset(dataset.keys())
    conf = start_conf
    min_confs = []
    rules_found = []
    supports = {}
    skyline_freq_isets = get_skyline(apriori(dataset, items, supp, supports))
    with open(text_filename, 'w') as file :
        while True:
            rules = gen_rules(skyline_freq_isets, dataset, conf, supports)
            min_confs.append(conf)
            rules_found.append(len(rules))
            file.write("{:08f} -> {}\n".format(conf, len(rules)))
            print("  {:08f} -> {}".format(conf, len(rules)))
            conf -= dx
            if conf - dx < end_conf:
                break
    plt.clf()
    plt.plot(min_confs, rules_found)
    plt.xlabel("minimum confidence value")
    plt.ylabel("rules found")
    plt.text(2, 2, "min_supp={}".format(supp))
    plt.savefig(plot_filename)


def write_named_freq_isets(filename, freq_isets, names):
    with open(filename, 'w') as file:
        freq_isets = sorted(freq_isets, key=lambda i: -i[0])
        file.write('Skyline Frequent Itemsets ({})\n'.format(len(freq_isets)))
        for s in freq_isets:
            first = next(iter(names))
            if 'Flavor' in names[first] and 'Food' in names[first]:
                named_set = { names[i]['Flavor'] + ' ' + names[i]['Food'] for i in s[1] }
            else:
                named_set = { names[i] for i in s[1] }
            file.write("({:03f}) {:>12}\n".format(s[0], str(named_set)))


def write_named_freq_isets_transcription(filename, freq_isets, genes, factors):
    with open(filename, 'w') as file:
        freq_isets = sorted(freq_isets, key=lambda i: -i[0])
        file.write('Skyline Frequent Itemsets ({})\n'.format(len(freq_isets)))
        for s in freq_isets:
            pass
            #first = next(iter(names))
            #named_set = { names[i]['Flavor'] + ' ' + names[i]['Food'] for i in s[1] }
            #file.write("({:03f}) {:>12}\n".format(s[0], str(named_set)))


def write_named_rules(filename, rules, names):
    with open(filename, 'w') as file:
        rules = sorted(rules, key=lambda r: -r[0])
        file.write('Skyline Rules ({})\n'.format(len(rules)))
        for r in rules:
            first = next(iter(names))
            if 'Flavor' in names[first] and 'Food' in names[first]:
                named_left = { names[i]['Flavor'] + ' ' + names[i]['Food'] for i in r[1][0] }
                named_right = { names[i]['Flavor'] + ' ' + names[i]['Food'] for i in r[1][1] }
            else:
                named_left = { names[i] for i in r[1][0] }
                named_right = { names[i] for i in r[1][1] }
 
            rule_str = "{} --> {}".format(named_left, named_right)
            file.write("({:03f}) {:>12}\n".format(r[0], rule_str))


def plot(baskets, names, min_supp):
    start_sup = 0.4  # when to start plot
    end_sup = 0.007 # when to end plot (eventually becomes too slow)
    start_conf = 1.0 # when to start plot
    end_conf = 0.3 # when to end plot
    print("plotting supports...")
    plot_supp("support.png", "support.txt", baskets, start_sup, end_sup)
    print("  -> wrote to support.png, support.txt")
    print("plotting confidences...")
    plot_conf("confidence.png", "confidence.txt", baskets, min_supp, start_conf, end_conf)
    print("  -> wrote to confidence.png, confidence.txt")
 
 
import argparse
from sys import argv
 
"""
Generates:
    (1) Plot file and text file of for found item sets for supports in a given range
    (2) Plot file and text file of for found rules for confidences in a given range
    (3) List of skyline frequent item sets in named form
    (4) List of skyline rules in named form
"""
def parse_normal(args):
    baskets = parse_data_file(args.data_file)
    names = parse_name_file(args.name_file)

    if args.plot:
        plot(baskets, names, args.min_supp)

    print("generating freq isets...")
    supports = {}
    items = frozenset(baskets.keys())
    freq_isets = apriori(baskets, items, args.min_supp, supports)
    sky_freq_isets = get_skyline(freq_isets)
    freq_isets_w_support = [(support(baskets, frozenset(s), supports), s) for s in sky_freq_isets]
    write_named_freq_isets("freq_isets.txt", freq_isets_w_support, names)
    print("  -> wrote to freq_isets.txt")

    if args.rules:
        print("generating rules...")
        rules = gen_rules(sky_freq_isets, baskets, args.min_conf, supports)
        rules_w_conf = [(confidence(baskets, r[0], r[1], supports), r) for r in rules]
        write_named_rules("rules.txt", rules_w_conf, names)
        print("  -> wrote to rules.txt")

def parse_ts(args):
    baskets, genes, factors = parse_t(args.data_file, args.name_file, args.factors)
    if args.plot:
        plot(baskets, factors, args.min_supp)
    
    print("generating freq isets...")
    supports = {}
    items = frozenset(baskets.keys())
    freq_isets = apriori(baskets, items, args.min_supp, supports)
    sky_freq_isets = get_skyline(freq_isets)
    freq_isets_w_support = [(support(baskets, frozenset(s), supports), s) for s in sky_freq_isets]
    write_named_freq_isets("freq_isets.txt",freq_isets_w_support,factors)
    print("  -> wrote to freq_isets.txt")

    if args.rules:
        print("generating rules...")
        rules = gen_rules(sky_freq_isets, baskets, args.min_conf, supports)
        rules_w_conf = [(confidence(baskets, r[0], r[1], supports), r) for r in rules]
        write_named_rules("rules.txt", rules_w_conf, factors)
        print("  -> wrote to rules.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", help="file containing the dataset")
    parser.add_argument("min_supp", type=float, help="minimum support, must be in range 0-1")
    parser.add_argument("min_conf", type=float, help="minimum confidence, must be in range 0-1")
    parser.add_argument("name_file", help="file that maps IDs in data file to names")

    parser.add_argument("--factors", help="specificy this to the factors name file and include the gene file as name file in order to analyze transcriptions")
    parser.add_argument("--rules", action='store_true', help="specify to generate association rules")
    parser.add_argument("--plot", action='store_true', help="specify to generate plots for min_supp and min_conf (warning: this makes the program very slow)")
    args = parser.parse_args()

    if args.factors:
        parse_ts(args) 
    else:
        parse_normal(args)

