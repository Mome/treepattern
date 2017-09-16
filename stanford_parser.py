import os
import argparse

from nltk.parse import stanford
import nltk

'~/.local/stanford-parser-full-2017-06-09'

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="Stanford parser path")
parser.add_argument("text")
args = parser.parse_args()

stanford_path = os.path.expanduser(args.path)
os.environ['STANFORD_MODELS'] = stanford_path
os.environ['STANFORD_PARSER'] = stanford_path
stanford_parser = stanford.StanfordParser()

sents = nltk.sent_tokenize(args.text)
trees = stanford_parser.raw_parse_sents(sents)

for tree in trees:
    print(list(tree)[0][0])
