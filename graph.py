from collections import namedtuple

class ConceptualGraph:

    Node = namedtuple('Node', ['id_', 'label', 'type', 'subgraph'])
    Edge = namedtuple('Edge', ['left', 'right'])

    type_map = {
        'relation' : 'shape=polygon',
        'statement' : 'shape=box',
        'process' : 'shape=parallelogram',
        'property' : 'shape=plaintext',
        None : 'shape=ellipse'
    }

    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_edge(self, left, right):
        if left not in self.nodes:
            self.nodes.append(left)
        if right not in self.nodes:
            self.nodes.append(right)
        self.edges.append(ConceptualGraph.Edge(left, right))

    def get_by_id(self, id_):
        for node in self.nodes:
            if node.id_ == id_:
                return node

    def to_dot(self):
        dot_code = ['digraph{', 'rankdir=LR', 'compound=true']

        cluster_dict = {n.subgraph:[] for n in self.nodes}
        for n in self.nodes:
            if n.id_ in cluster_dict:
                continue
            cluster_dict[n.subgraph].append(n.id_)


        subgraphs = {}

        for node in self.nodes:
            label = 'label=' + '"' + node.label + '"'
            type_ = ConceptualGraph.type_map[node.type]
            content = ', '.join([label, type_])
            line = ['N' + str(node.id_), '[', content, ']']
            line = ' '.join(line)
            if node.subgraph is None:
                dot_code.append(line)
            else:
                if node.id_ in cluster_dict:
                    continue
                if node.subgraph in subgraphs:
                    subgraphs[node.subgraph].append(line)
                else:
                    subgraphs[node.subgraph] = [line]

        for name, lines in subgraphs.items():
            dot_code.append('subgraph cluster' + str(name) + '{')
            #dot_code.append('  ' + ConceptualGraph.type_map['statement'])
            for l in lines: dot_code.append('  ' + l)
            dot_code.append('}')

        for edge in self.edges:

            arrow_props = []

            left_id = edge.left.id_
            if left_id in cluster_dict:
                arrow_props.append('ltail=cluster'+str(left_id))
                left_id = choice(cluster_dict[left_id])
                
                                
            right_id = edge.right.id_
            if right_id in cluster_dict:
                arrow_props.append('lhead=cluster'+str(right_id))
                right_id = choice(cluster_dict[right_id])
                

            line  = ['N'+str(left_id), '->', 'N'+str(right_id)]
            if arrow_props:
                line.extend(['[',*arrow_props,']'])
            dot_code.append(' '.join(line))

        dot_code.append('}')

        return '\n'.join(dot_code)
