import csv, pdb, itertools
from pprint import pprint


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
    #for f1,f2 in (pair for pair in pairwise(F) if len(pair[0]) == len(pair[1]) == k):
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


"""
Rules2.xml

Rule 1:    1       ---> 49   [15, 95]
Rule 2:    15      ---> 36   [20, 95]
Rule 3:    9       ---> 22   [25, 95]
Rule 4:    12, 14  ---> 16   [30, 95]
"""

def rules_to_str(rules):
    return ["{} ---> {}".format(r[0], r[1]) for r in rules]



if __name__ == "__main__":
    baskets = parse_bakery('../dataset/example/out1.csv')
    min_sup = 0.13
    min_conf = 0.79
    items = set(baskets.keys())
    supports = {}
    freq_isets = apriori(baskets, items, min_sup, supports)
    skyline_freq_isets = get_skyline(freq_isets)
    rules = gen_rules(skyline_freq_isets, baskets, min_conf, supports)
    print("minSupp={}, minConf={}".format(min_sup, min_conf))
    print("Skyline Sets: ", skyline_freq_isets)
    for r in rules_to_str(rules):
        print(r)


