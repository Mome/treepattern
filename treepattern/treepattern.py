import logging
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Set logging level to 'DEBUG'.")
    parser.add_argument("--info", action="store_true", help="Set logging level to 'INFO'.")
    parser.add_argument("rules", help="File with rules.")
    parser.add_argument("sents", help="English sentences.")
    return parser.parse_args()


def main():
    args = parse_args()
    
    
    if args.debug:
        level = logging.DEBUG
    elif args.info:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)
    
    
    # set Stanford parser and model path
    parser_path = os.environ['STANFORD_PARSER']
    parser_path = os.path.expanduser(parser_path)
    os.environ['STANFORD_PARSER'] = parser_path
        
    if 'STANFORD_MODELS' in os.environ:
        models_path = os.environ['STANFORD_MODELS']
        models_path = os.path.expanduser(models_path)
        os.environ['STANFORD_MODELS'] = models_path
    else:
        os.environ['STANFORD_MODELS'] = os.environ['STANFORD_PARSER']
       
    
    with open(args.rules) as f:
        rules = f.read()
 

    from matcher import PatternMatcher 
    matcher = PatternMatcher.from_str(rules)
    
    from builder import GraphBuilder
    builder = GraphBuilder(matcher)
    
    for graph in builder.build(args.sents):
        dot_code = graph.to_dot()
        print(dot_code)

        
if __name__ == '__main__':
    main()
  

"""from parse import parse_tree_str
tree = parse_args().tree
tree = parse_tree_str(tree)

print(tree)"""


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
