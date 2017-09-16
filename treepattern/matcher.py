from collections import namedtuple
import logging

from parse import RuleParser

class PatternMatcher:

    Match = namedtuple('Match', ['prop_tree', 'rule', 'head_match',
                                 'pattern_match', 'relations', 'transformation'])

    def __init__(self, rules, whole=True, head_only_ones=True):
        self.rules = rules
        self.whole = whole
        self.head_only_ones = head_only_ones


    def match(self, sents):
        """Constructs PropertyTrees from text and passes to match_rules"""

        if isinstance(sents, str):
            sents = [
                nltk.word_tokenize(s)
                for s in nltk.sent_tokenize(sents)
            ]

        logging.info('Construnct parsetree for all sentences!')
        parse_trees = stanford_parser.parse_sents(sents)

        for pt, sent in zip(parse_trees, sents):

            pt = list(pt)[0][0] # convert to list get tree and remove root node

            #pt.draw()
            logging.debug('ParseTree:' + pformat(pt))

            logging.info('Construct property trees from parsetrees!')
            prop_tree = PropertyTree.from_parsetree(pt)
            add_properties(prop_tree)
            logging.debug(str(prop_tree))

            yield from self.match_rules(prop_tree)


    def match_rules(self, prop_tree):

        if self.head_only_ones:
            matched_nodes = [] # list of roots that have already been matched

        for rule in self.rules:

            head, pattern, _, _ = rule

            for head_node in prop_tree.descendant_or_self():

                satisfies_constaints = head_node.has_properties(**head.constraints)

                logging.debug(
                    'HEAD_TRY:\n Constraints: %s\n Properties: %s\n> %s!'
                    %(str(head.constraints), str(head_node.properties),
                        'YES!' if satisfies_constaints else 'NO!'))

                if not satisfies_constaints:
                    continue
                if self.head_only_ones and head_node in matched_nodes:
                    continue

                if self.whole:
                    start_nodes = head_node.no_preceding()
                else:
                    start_nodes = head_node.descendant_or_self()

                for match in self._search(start_nodes, pattern, head_node):

                    # TODO -- check for double varnames ?
                    match_dict = dict(match)
                    match_dict[head.varname] = head_node

                    relations = [
                        (match_dict[left], match_dict[right])
                        for left, right in rule.relations
                        ]

                    transformation = (
                        head_node,
                        match_dict[rule.transformation] if rule.transformation in match_dict else rule.transformation
                        )
                    head_match = (head.varname, head_node)

                    yield PatternMatcher.Match(
                        prop_tree, rule, head_match,
                        match, relations, transformation)

                    if self.head_only_ones:
                        matched_nodes.append(head_node)
                        break


    def _search(self, nodes, pattern, head_node, match=None, index=0):

        if match is None:
            match = [None]*len(pattern)

        if len(pattern) == index:
            if self.whole:
                nodes = list(nodes)

            if self.whole and len(nodes):
                #print(nodes, index)
                logging.debug('Match, but not whole.')
            else:
                logging.info('Pattern matched: '
                    + head_node['label']
                    + ' : '
                    + str([pt.varname for pt in pattern]))
                yield tuple(match)

        else:
            varname, constraints = pattern[index]

            for node in nodes:

                satisfies_constaints = node.has_properties(**constraints)

                logging.debug(
                        'PATTERN_TRY:%i\n Constraints: %s\n Properties: %s\n> %s!'
                        %(index, str(constraints), str(node.properties),
                            'YES!' if satisfies_constaints else 'NO!'))

                if not satisfies_constaints:
                    continue

                match[index] = (varname, node) # assign node to variable

                imidiate_following = node.imidiate_following(root=head_node)

                yield from self._search(imidiate_following, pattern, head_node, match, index+1)


    @classmethod
    def from_str(cls, rules_str):
        parser = RuleParser()
        rules = parser.parse_rules(rules_str)
        return cls(rules)

    class PatternMatchingError(Exception):
        pass
