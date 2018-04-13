import csv, pdb, itertools
from pprint import pprint
import matplotlib.pyplot as plt
import math

def parse_bakery(filename):
    baskets = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            baskets[int(row[0])] = set(map(lambda x: int(x), row[1:]))
    return baskets

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
        if len(f1) != k:
            continue
        for f2 in F:
            if len(f1) != len(f2):
                continue
            c = f1.union(f2)
            if len(c) == len(f1) + 1:
                flag = True
                for s in powerset(c):
                    if len(s) == len(c) - 1 and (set(s) not in F):
                        flag = False
                if flag:
                    candidates.append(c)
    return candidates

def apriori(T, I, min_sup, supports):
    freq_sets = [[], [frozenset({i}) for i in I if support(T, {i}, supports) >= min_sup]]
    k = 2
    while freq_sets[k-1]:
        candidates = candidates_gen(freq_sets[k-1], k-1)
        counts = {c: 0 for c in candidates}
        for _, basket in T.items():
            for c in (c for c in candidates if c.issubset(basket)):
                counts[c] += 1
        freq_sets.append([c for c in candidates if (counts[c]/len(T) >= min_sup)])
        k += 1
    return [set(f) for fs in freq_sets for f in fs]

def get_skyline(F):
    uniq = {frozenset(s) for s in F}
    skyline = []
    while uniq:
        s = uniq.pop()
        if all((not s.issubset(s1) for s1 in skyline)):
            skyline.append(set(s))
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

def rules_to_str(rules):
    return ["{} ---> {}".format(r[0], r[1]) for r in rules]

def plot_supp(dataset, supp_init, cutoff):
    dx = 0.005
    items = frozenset(dataset.keys())
    min_supports = []
    isets_found = []
    supp = supp_init
    supports = {}
    while True:
        freq_isets = get_skyline(apriori(dataset, items, supp, supports))
        print("supp({}) -> {}".format(supp, len(freq_isets)))
        min_supports.append(supp)
        isets_found.append(len(freq_isets))
        supp -= dx
        if supp - dx < cutoff:
            print("supp too low, ending")
            break
    plt.plot(min_supports, isets_found)
    plt.xlabel("minimum support value")
    plt.ylabel("freq item sets found")
    plt.savefig("../support.png")


def plot_conf(dataset, supp, conf_init, cutoff):
    dx = 0.005
    items = frozenset(dataset.keys())
    min_confs = []
    rules_found = []
    conf = conf_init
    supports = {}
    skyline_freq_isets = get_skyline(apriori(dataset, items, supp, supports))
    while True:
        rules = gen_rules(skyline_freq_isets, baskets, conf, supports)
        print("rules({}) -> {}".format(conf, len(rules)))
        min_confs.append(conf)
        rules_found.append(len(rules))
        conf += dx
        if conf + dx > cutoff:
            print("conf too high, ending")
            break
    plt.plot(min_confs, rules_found)
    plt.xlabel("minimum confidence value")
    plt.ylabel("rules found")
    plt.text(.75, .75, "min_supp={}".format(supp))
    plt.savefig("../confidence.png")



"""
lab-2-example-output

Rule 1:     36   ---> 15    [sup=13.886113   conf=79.88506]
Rule 2:     15   ---> 36    [sup=13.886113   conf=75.13513]
Rule 3:     22   ---> 9    [sup=18.081919   conf=84.18605]
Rule 4:     9   ---> 22    [sup=18.081919   conf=80.44444]
Rule 5:     49   ---> 1    [sup=12.687312   conf=78.395065]
Rule 6:     1   ---> 49    [sup=12.687312   conf=81.410255]
Rule 7:     14, 16   ---> 12    [sup=25.674326   conf=99.612404]
Rule 8:     12, 16   ---> 14    [sup=25.674326   conf=99.2278]
Rule 9:     12, 14   ---> 16    [sup=25.674326   conf=95.89552]
"""


if __name__ == "__main__":
    baskets = parse_bakery('../dataset/example/out1.csv')
    #items = frozenset(baskets.keys())
    #supports = {}
    #freq_isets = apriori(baskets, items, min_sup, supports)
    #skyline_freq_isets = get_skyline(freq_isets)
    #rules = gen_rules(skyline_freq_isets, baskets, min_conf, supports)
    #plot_supp(baskets, 0.3, 0.0261)
    #plot_conf(baskets, 0.16, 0.5, 1.0)


