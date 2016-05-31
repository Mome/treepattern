from builder import GraphBuilder
from matcher import PatternMatcher
import logging
import sys


args=sys.argv[1:]

if not args:
    raise Warning('Need sentences!')
    sys.exit(0)

logging.basicConfig(level=logging.INFO)

sents = args[0]

with open('rules') as f:
    rules = f.read()

matcher = PatternMatcher.from_str(rules)
builder = GraphBuilder(matcher)

for graph in builder.build(sents):
    dot_code = graph.to_dot()
    print(dot_code)

"""print()
print()
print('Check matches first!!!')
for match in matcher.match(sent):
    prop_tree, rule, head_match, pattern_match, _r, _t  = match

    hm_varname,  hm_node  = head_match
    pm_varnames, pm_nodes = zip(*pattern_match)

    hm_label = hm_node['label']
    pm_labels = [n['label'] for n in pm_nodes]

    hm_term = hm_node['terminal']
    pm_terms = [n['terminal'] for n in pm_nodes]

    print()
    print(sent)
    print(' ', hm_varname, '\t| ', '\t'.join(pm_varnames))
    print(' ', hm_label, '\t| ', '\t'.join(pm_labels))
    print()
    print(hm_label, '▶', hm_term)
    for L,T in zip(pm_labels, pm_terms):
        print(L, '▶', T)

    input()"""
