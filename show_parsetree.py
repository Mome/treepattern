import os
import sys

import nltk
from nltk.parse import stanford

stanford_path = os.path.expanduser('~/.local/stanford-parser')
os.environ['STANFORD_MODELS'] = stanford_path
os.environ['STANFORD_PARSER'] = stanford_path
stanford_parser = stanford.StanfordParser()

from utils import proptree_to_dot
from trees import PropertyTree
from builder import add_properties


sents = " ".join(sys.argv[1:])

sents = [
    nltk.word_tokenize(s)
    for s in nltk.sent_tokenize(sents)
]

parse_trees = stanford_parser.parse_sents(sents)

for pt, sent in zip(parse_trees, sents):
	pt = list(pt)[0][0]
	proptree = PropertyTree.from_parsetree(pt)
	add_properties(proptree)
	dot_code = proptree_to_dot(proptree)
	print(dot_code)