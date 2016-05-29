from itertools import product

def partialsort(elements, cmp):
    """Bubblesort to deal with partial orders."""

    L = list(elements)
    for i,j in product(range(len(L)), repeat=2):
        if cmp(L[i], L[j]) > 0:
            L[i], L[j] = L[j], L[i]
    return L

def proptree_to_dot(proptree):

    postags = []
    terminals = []
    nodelines = []
    edgelines = []

    def construct_substrees(node):
        nid = 'N'+str(id(node))
        #print(node.properties)
        nl = nid + ' [label="' + node['label'] + '"]'
        nodelines.append(nl)
        if node.children:
            for c in node.children:
                el = nid + ' -> ' + 'N'+str(id(c))
                edgelines.append(el)
                construct_substrees(c)
        else:
            postags.append(nid)
            tid = 'T'+str(len(terminals))
            el = nid + ' -> ' + tid
            edgelines.append(el)
            nl = tid + ' [shape=box, label="' + node['terminal'] + '"]'
            nodelines.append(nl)
            terminals.append(tid)

    construct_substrees(proptree)

    return '\n'.join([
        'digraph PropTree{',
        *nodelines,
        *edgelines,
        '{ rank=same; ' + ', '.join(postags) + '}',
        '{ rank=same; ' + ', '.join(terminals) + '}',
        '}',
    ])



def property_tree_to_dot(tree) :
    """ Transforms a propertytrees in a digraph dotcode"""
    
    dot_code = 'digraph graphname {\n'
    dot_code += str(0) + ' [label="' + tree.label() + '"];\n'

    def get_subtrees(tree, node_number=0, terminals = '{ rank=same; '):
        dot_code = ""

        father_node_number = node_number

        for child in tree:

            node_number+=1

            if isinstance(child,str) :
                dot_code += str(node_number) + ' [label="' + child + '" shape=box];\n'
                dot_code += str(father_node_number) + ' -> ' + str(node_number) + '\n'
                terminals += str(node_number) + '; '
            else :
                dot_code += str(node_number) + ' [label="' + child.label() + '"];\n'
                dot_code += str(father_node_number) + ' -> ' + str(node_number) + '\n'
                new_code, node_number, terminals = get_subtrees(child,node_number,terminals)
                dot_code += new_code

        return dot_code, node_number, terminals

    new_code, _, terminals = get_subtrees(tree)
    dot_code += terminals + '}\n'
    dot_code += new_code + '}'

    return dot_code
    