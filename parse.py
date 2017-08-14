from pyparsing import *
from collections import namedtuple

constituent_list = """S SBAR SBARQ SINV SQ ADJP ADVP CONJP FRAG INTJ LST NAC NP
NX PP PRN PRT QP RRC UCP VP WHADJP WHAVP WHNP WHPP X CC CD DT EX FW IN JJ JJR
JJS LS MD NN NNS NNP NNPS PDT POS PRP PRP$ RB RBR RBS RP SYM TO UH VB VBD VBG
VBN VBP VBZ WDT WP WP$ WRB , .""".split()

constituent_macros = {
    'V'  : 'VB VBD VBG VBN VBP VBZ'.split(),
    'N'  : 'NN NNS NNP NNPS'.split(),
    'W'  : 'WHADJP WHAVP WHNP WHPP'.split(),
    'SS' : 'S SBAR SBARQ SINV SQ'.split(),
    'J'  : 'JJ JJR JJS'.split(),
}

class RuleParser:

    PatternToken = namedtuple('PatternToken',['varname','constraints'])
    Rule = namedtuple('Rule', ['head', 'pattern', 'relations', 'transformation'])


    def __init__(self):
        nonums = alphas + '.!?$_§@,;'
        singel_constraint_value = Word(alphanums).setResultsName('value')

        constraint_value = Group(
            singel_constraint_value |
            Suppress('{')
                + singel_constraint_value
                + ZeroOrMore(Suppress('|') + singel_constraint_value)
                + Suppress('}')
        ).setResultsName('value_set')

        constraint = Group(
            Word(alphanums).setResultsName('key')
            + Suppress('=')
            + constraint_value
        ).setResultsName('constraint')

        constraint_list = Group(
            Suppress('[')
            + constraint
            + ZeroOrMore(Suppress('|') + constraint)
            + Suppress(']')
        ).setResultsName('constraints_list')

        p_token = Group(
            Word(nonums).setResultsName('alpha')
            + Optional(Word(nums)).setResultsName('num')
            + Optional(constraint_list)
        ).setResultsName('token')

        pattern = Group(ZeroOrMore(p_token)).setResultsName('pattern')

        #arg = Word(alphanums).setResultsName('arg')
        #arguments = Group(arg + ZeroOrMore(Suppress(',') + arg)).setResultsName('arglist')
        #predicate = Word(alphanums).setResultsName('name') + Suppress('(') + Optional(arguments) + Suppress(')')
        #predicate_list = Group(Optional(predicate + ZeroOrMore(',' + predicate))).setResultsName('predicate_list')

        relation = Group(
            Word(nonums + nums).setResultsName('left')
            + Suppress(oneOf('-> -'))
            + Word(nonums + nums).setResultsName('right')
            ).setResultsName('relation')
        relation_list = Group(relation + ZeroOrMore(relation)).setResultsName('relation_list')

        transformation = Word(nonums + nums).setResultsName('transformation')

        rule = Group(
            p_token.setResultsName('head')
            + Suppress(':')
            + pattern
            + Suppress(':')
            + Optional(relation_list)
            + Suppress(':')
            + Optional(transformation)
        ).setResultsName('rule')

        rule.ignore( pythonStyleComment )

        self._parser = rule


    def parse_rules(self, rules_str):
        parser = self._parser

        rules = []
        for line in rules_str.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parsetree = parser.parseString(line).rule
            head = self.__class__._construct_ptoken(parsetree.head)
            pattern = [self.__class__._construct_ptoken(pt) for pt in parsetree.pattern]
            relations = [(left, right) for left, right in parsetree.relation_list]
            transformation = parsetree.transformation
            rules.append(self.__class__.Rule(head, pattern, relations, transformation))
        return rules


    @classmethod
    def _construct_ptoken(cls, ptoken):
        constraint_dict = {}
        if ptoken.alpha in constituent_list:
            constraint_dict['label'] = {ptoken.alpha}
        elif ptoken.alpha in constituent_macros:
            labels = constituent_macros[ptoken.alpha]
            constraint_dict['label'] = set(labels)
        elif not ptoken.alpha.isupper():
            constraint_dict['terminal'] = {ptoken.alpha}

        for key, value_set in ptoken.constraints_list:
            value_set = set(value_set)
            if key in constraint_dict:
                constraint_dict[key].update(value_set)
            else:
               constraint_dict[key] = value_set
        return cls.PatternToken(ptoken.alpha + ptoken.num, constraint_dict)


def parse_tree_str(tree):
    """Turns a phrase structure tree output from Stanford Parser into a list of lists."""

    if type(tree) is str:
        tree = tree.replace('\n', ' ')
        tree = tree.replace('(',' ( ')
        tree = tree.replace(')',' ) ')
        tokens = filter(None, tree.split(' '))
    else:
        tokens = tree

    out = []

    for tok in tokens:
        if tok == '(':
            subtree = parse_tree_str(tokens)
            out.append(subtree)
        elif tok == ')':
            break
        else:
            out.append(tok)

    return out

# filter should be like this
"""_filter = filter
def filter(iterable, func=None):
    return _filter(func, iterable)"""
