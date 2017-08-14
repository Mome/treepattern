from itertools import chain, count
from pprint import pformat
import os
import logging

from utils import partialsort
from trees import PropertyTree
from parse import constituent_macros
from graph import ConceptualGraph

relation_constituents = ['IN', 'TO']
statement_constituents = constituent_macros['SS'] + constituent_macros['W']
property_constituents = constituent_macros['J']
process_constituents = constituent_macros['V'] + ['VP']


def contsituen2type(const):
    if const in relation_constituents:
        return 'relation'
    if const in statement_constituents:
        return 'statement'
    if const in property_constituents:
        return 'property'
    if const in process_constituents:
        return 'process'

class GraphBuilder:

    def __init__(self, pattern_matcher):
        self.pattern_matcher = pattern_matcher

    def build(self, sents):

        # tokenize sentences
        if isinstance(sents, str):
            sents = sents.lower() # convert to lower case !!!
            sents = [
                nltk.word_tokenize(s)
                for s in nltk.sent_tokenize(sents)
            ]

        logging.info('Construnct parsetree for all sentences!')
        parse_trees = stanford_parser.parse_sents(sents)

        for pt, sent in zip(parse_trees, sents):

            pt = list(pt)[0][0] # convert to list get tree and remove root node

            #import threading; threading.Thread(None, pt.draw).start()
            # pt.draw()

            logging.debug('ParseTree:' + pformat(pt))

            logging.info('Construct property trees from parsetrees!')
            prop_tree = PropertyTree.from_parsetree(pt)
            add_properties(prop_tree)
            logging.debug(str(prop_tree))

            tmp_list = [
                (match.relations, match.transformation)
                for match in self.pattern_matcher.match_rules(prop_tree)]

            if len(tmp_list) == 0:
                logging.info('No match for: "' + ' '.join(sent) + '"')
                continue

            relations, transformations = zip(*tmp_list)

            trans_dict = dict(transformations)
            trans_dict = {
                key : trans_dict[value] if value in trans_dict else value
                for key, value in trans_dict.items()}

            # find self translations to construct subgraphs
            subgraph_roots = [k for k,v in trans_dict.items() if k is v]
            subgraph_roots = partialsort(subgraph_roots, PropertyTree.cmp)

            transformed_relations = []
            for left, right in chain(*relations):
                if left in trans_dict:
                    left = trans_dict[left]
                if right in trans_dict:
                    right = trans_dict[right]
                transformed_relations.append((left, right))

            graph = ConceptualGraph()

            id_counter = count()
            for left, right in transformed_relations:

                left_id = next(id_counter) if isinstance(left, str) else id(left)
                right_id = next(id_counter) if isinstance(right, str) else id(right)

                left_node = graph.get_by_id(left_id)
                right_node = graph.get_by_id(right_id)

                # decide if nodes are part of subgraph
                if None in (left_node, right_node):
                    left_subgraph, right_subgraph = None, None
                    if isinstance(right, str):
                        logging.warn('String destination for subgraphs not implemented yet:' + tmp_right)
                    else:
                        for sgr in subgraph_roots:
                            if right in sgr.descendant_or_self():
                                right_subgraph = id(sgr)
                                if isinstance(left, str):
                                    left_subgraph = id(sgr)
                                break
                    if not isinstance(left, str):
                        for sgr in subgraph_roots:
                            if left in sgr.descendant_or_self():
                                left_subgraph = id(sgr)
                                break

                if left_node is None:
                    left_node = ConceptualGraph.Node(
                        id_=left_id,
                        label=left if isinstance(left, str) else left['terminal'],
                        type=contsituen2type(None if isinstance(left, str) else left['label']),
                        subgraph=left_subgraph)


                if right_node is None:
                    right_node = ConceptualGraph.Node(
                        id_=right_id,
                        label=right if isinstance(right, str) else right['terminal'],
                        type=contsituen2type(None if isinstance(right, str) else right['label']),
                        subgraph=right_subgraph)

                graph.add_edge(left_node, right_node)

            # whenever something references a cluster
            #(node transforming to itself)
            # refer to random node of luster instead
            #(since clusters cannot be referenced in dot)

            yield graph


def add_properties(prop_tree):
    for node in prop_tree.descendant_or_self():
        node.properties['terminal'] = node.terminals
