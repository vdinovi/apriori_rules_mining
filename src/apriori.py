import csv, pdb, itertools

def parse_bakery(filename):
    baskets = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            baskets[int(row[0])] = set(map(lambda x: int(x), row[1:-1]))
    return baskets

def support(T, item_set):
    x_subset_basket = 0
    for _, basket in T.items():
        if item_set.issubset(basket):
            x_subset_basket += 1 
    return x_subset_basket / len(T)

def confidence(T, antecedent, consequent):
    return support(T, antecedence.union(consequent)) / support(T, antecedent)

# From itertools recipe "pairwise"
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

# From itertools recipe "powerset"
def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def candidates_gen(f, k):
    candidates = []
    for f1, f2 in pairwise(f):
        if len(f1) != k or len(f2) != k:
            continue
        c = frozenset(f1.union(f2))
        if len(c) != len(f1) + 1:
            continue
        flag = True
        for s in powerset(c):
            if len(s) == len(c) - 1 and (set(s) not in f):
                flag = False
        if flag:
            candidates.append(c)
    return candidates

def apriori(T, I, min_sup):
    freq_sets = []
    freq_sets.append([frozenset([i]) for i in I if support(T, {i}) >= min_sup])
    k = 2
    while freq_sets[-1]:
        candidates = candidates_gen(freq_sets[-1], k-1)
        counts = {c: 0 for c in candidates}
        for _, basket in T.items():
            cands = [c for c in candidates if c.issubset(basket)]
            for c in cands:
                counts[c] += 1
        freq_sets.append([c for c in candidates if (counts[c]/len(T) >= min_sup)])
        k += 1
    return freq_sets



def gen_rules(F, min_conf):
    rules = []
    for f in F:
        base = []
        for s in f:
            a = f.difference(s)
            b = s
            if confidence(T, a, b) >= min_conf:
                base.append((a, b))
        rules += apGenRules(f, base)
    return rules


def test(baskets, cases):
    #freq_itemsets = apriori(baskets, case[2], case[0])
    #rules = gen_rules(freq_itemsets, minconf)
    #actual   = ["{} --> {}".format(r[0], r[1]) for r in rules]
    #expected = ["{} --> {}".format(r[2], r[3]) for r in rules]
    #print("(sup={}, conf={}) found {} --> {}, expected {} --> {}".format()



if __name__ == "__main__":
    baskets = parse_bakery('../dataset/1000/1000-out1.csv')
    item_set = [1,2,3]
    min_sup = 0.1
    min_conf = 0.5
    #cases = [
    #        (.15, .95, ({1},     {49}),
    #        (.20, .95, ({15},    {36}), 
    #        (.25, .95, ({9},     {22}), 
    #        (.30, .95, ({12,14}, {16})
    #]
    #for i in cases:
    #    test(baskets, i)
    freq_itemsets = apriori(baskets, item_set)
    rules = gen_rules(freq_itemsets, min_conf)

