import csv, pdb, itertools
from pprint import pprint
import matplotlib.pyplot as plt
import math

def parse_data_file(filename):
    baskets = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            baskets[int(row[0])] = set(map(lambda x: int(x), row[1:]))
    return baskets

def parse_name_file(filename):
    result = {}
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = int(row.pop('Id'))
            if key in result:
                pass
            result[key] = row
    return result

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

def plot_supp(plot_filename, text_filename, dataset, start_supp, end_supp):
    dx = 0.001
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
            file.write("  {:08f} -> {}\n".format(supp, len(freq_isets)))
            supp -= dx
            if supp - dx < end_supp:
                break
    plt.clf()
    plt.plot(min_supports, isets_found)
    plt.xlabel("minimum support value")
    plt.ylabel("freq item sets found")
    plt.savefig(plot_filename)


def plot_conf(plot_filename, text_filename, dataset, supp, start_conf, end_conf):
    dx = 0.001
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
            file.write("  {:08f} -> {}\n".format(conf, len(rules)))
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
            named_set = { names[i]['Food'] for i in s[1] }
            file.write("({:03f}) {:>12}\n".format(s[0], str(named_set)))

def write_named_rules(filename, rules, names):
    with open(filename, 'w') as file:
        rules = sorted(rules, key=lambda r: -r[0])
        file.write('Skyline Rules ({})\n'.format(len(rules)))
        for r in rules:
            named_left = { names[i]['Food'] for i in r[1][0] }
            named_right = { names[i]['Food'] for i in r[1][1] }
            rule_str = "{} --> {}".format(named_left, named_right)
            file.write("({:03f}) {:>12}\n".format(r[0], rule_str))

"""
Generates:
    (1) Plot file and text file of for found item sets for supports in a given range
    (2) Plot file and text file of for found rules for confidences in a given range
    (3) List of skyline frequent item sets in named form
    (4) List of skyline rules in named form
"""
def mine_bakery(data_filename, goods_filename):
    # Change these as needed
    start_sup = 0.2  # when to start plot
    end_sup = 0.0 # when to end plot (eventually becomes too slow)
    min_sup = 0.0135 # actual min support (derived from analysis)
    start_conf = 1.0 # when to start plot
    end_conf = 0.5 # when to end plot
    min_conf = 0.828  # actual min confidence

    baskets = parse_data_file(data_filename)
    names = parse_name_file(goods_filename)
    print("plotting supports...")
    plot_supp("support.png", "support.txt", baskets, start_sup, end_sup)
    print("plotting confidences...")
    plot_conf("confidence.png", "confidence.txt", baskets, min_sup, start_conf, end_conf)

    print("generating rules...")
    supports = {}
    items = frozenset(baskets.keys())
    freq_isets = apriori(baskets, items, min_sup, supports)
    sky_freq_isets = get_skyline(freq_isets)
    rules = gen_rules(sky_freq_isets, baskets, min_conf, supports)

    freq_isets_w_support = [(support(baskets, frozenset(s), supports), s) for s in sky_freq_isets]
    print("writing freq isets...")
    write_named_freq_isets("freq_isets.txt", freq_isets_w_support, names)
    print("writing rules...")
    rules_w_conf = [(confidence(baskets, r[0], r[1], supports), r) for r in rules]
    write_named_rules("rules.txt", rules_w_conf, names)

if __name__ == "__main__":
    mine_bakery('../dataset/1000/1000-out1.csv', '../dataset/goods.csv')
 





