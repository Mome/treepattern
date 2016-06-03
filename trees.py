from itertools import takewhile, islice, dropwhile
from math import ceil, floor

class IteratorTree:
    def __init__(self, parent=None, children=None):
        self.children = []
        if children: self.add_children(*children)
        self.parent = parent

    def add_children(self, *children):
        for child in children: child.parent=self
        self.children += children

    def ancestor(self, root=None):
        if not (self is root):
            parent = self.parent
            while not (parent is root):
                if parent is None:
                    raise IteratorTree.RootNotFoundError()
                yield parent
                parent = parent.parent
            if root: yield root
            
    def ancestor_or_self(self, root=None):
        yield self
        yield from self.ancestor(root)

    def descendant(self):
        #return chain.from_iterable(
        #    child.descendant_or_self for child in self.children)
        return islice(self.descendant_or_self(), 1, None)

    def descendant_or_self(self):
        yield self
        for child in self.children:
            for des in child.descendant_or_self():
                yield des

    def sibling(self):
        yield from filter(self.__ne__, self.sibling_or_self())

    def sibling_or_self(self):
        if self.parent: yield from self.parent.children

    def following(self):
        for ancestor in self.ancestor_or_self():
            for fosib in ancestor.following_sibling():
                for follower in fosib.descendant_or_self():
                    yield follower

    def following_sibling(self):
        yield from islice(
            dropwhile(self.__ne__, self.sibling_or_self()), 1, None)

    def preceding(self):
        for ancestor in self.ancestor_or_self():
            for fosib in ancestor.preceding_sibling():
                yield from fosib.descendant_or_self()

    def preceding_sibling(self):
        yield from takewhile(self.__ne__, self.sibling_or_self())

    def imidiate_following(self, root=None):

        def next_sibling(node):
            if node!=root and node.parent and node.parent.children:
                i = node.parent.children.index(node)
                if len(node.parent.children) > i+1:
                    return node.parent.children[i+1]

        # find next sibling of ancestor or self
        for node in self.ancestor_or_self(root):
            next = next_sibling(node)
            if next:
                yield from next.no_preceding() # node and all firstborn
                break

    def no_preceding(self):
        yield self
        node = self
        while node.children:
            node = node.children[0]
            yield node

    def __str__(self):
        name = self.__class__.__name__
        if len(self.children)==0:
            return name
        inner = ' '.join(str(c) for c in self.children)        
        return ''.join([name, '[ ', inner, ']'])

    class RootNotFoundError(Exception):
        pass
            



class PropertyTree(IteratorTree):

    def __init__(self, parent=None, children=None, **keyargs):
        super(PropertyTree, self).__init__(parent, children)
        self.properties = keyargs
        self.small_world = True # everything unknown is false

        # add IteratorTree as properties
        for prop in IteratorTree.__dict__:
            ... # ???

    def __getitem__(self, key):
        return self.properties[key]

    @classmethod
    def from_parsetree(cls, nltktree, parent=None):
        if isinstance(nltktree, str):
            parent.properties['terminal'] = nltktree
            new_tree = None
        else:
            new_tree = PropertyTree(label=nltktree.label(), parent=parent)
            new_tree.children = [cls.from_parsetree(subtree, new_tree) for subtree in nltktree]
            new_tree.children = [x for x in new_tree.children if not x is None]
        return new_tree

    @property
    def terminals(self):
        if 'terminal' in self.properties:
            out = self.properties['terminal']
        else:
            out = ' '.join(c.terminals for c in self.children)
        return out


    def has_properties(self, **props):

        for key, value_set in props.items():
            if not (key in self.properties):
                if self.small_world:
                    break
                else:
                    continue

            if callable(self.properties[key]):
                self.properties[key] = self.properties[key]()

            if self.properties[key] not in value_set:
                break
        else:
            return True

        return False

    def cmp(self, node):
        if self in node.descendant():
            value = 1
        elif node in self.descendant():
            value = -1
        else:
            value = 0
        return value

    def __repr__(self):
        return self.__str__()
        

    def __str__(self):
        name = self.properties.get('label', self.__class__.__name__)
        if len(self.children)==0:
            return name + ' "' + self.terminals + '"'
        inner = ' '.join(str(c) for c in self.children)        
        return ''.join([name, '[ ', inner, ']'])

    def draw_to_ascii(self):
        lab = 'label' in self.properties
        ter = 'terminal' in self.properties
        if not self.children:
            if lab and ter:

                label = self.properties['label']
                terminal = '"'+self.properties['terminal']+'"'
                max_len = max(len(label), len(terminal))

                rmargin = ' '*ceil((max_len-len(label))/2)
                lmargin = ' '*floor((max_len-len(label))/2)
                label = rmargin + label + lmargin

                rmargin = ' '*ceil((max_len-len(terminal))/2)
                lmargin = ' '*floor((max_len-len(terminal))/2)
                terminal = rmargin + terminal + lmargin

                edge = [' ']*max_len
                edge[max_len//2] = '|'
                edge = ''.join(edge)

                out = '\n'.join([label, edge, terminal])

            elif lab:
                out = self.properties['label']
            elif ter:
                out = '"'+self.properties['terminal']+'"'
            else:
                out = '?'
        else:
            childlabels = [c.draw_to_ascii().split('\n') for c in self.children]
            
            # bring to same high
            max_depth = max(map(len, childlabels))
            for cl in childlabels:
                if len(cl) == max_depth:
                    continue
                edge = [' ']*max_len
                edge[max_len//2] = '|'
                edge = ''.join(edge)
                while len(cl) < max_depth:
                    pass
                




            raise NotImplementedError()

        return out