
class Node:
    _url = None
    _children = []
    _depth = None
    _lastmod = None

    def __init__(self, url, depth, lastmod):
        self._url = url
        self._depth = depth
        self._lastmod = lastmod

    def get_url(self):
        return self._url

    def get_depth(self):
        return self._depth

    def get_lastmod(self):
        return self._lastmod

    def get_num_children(self):
        return len(self._children)

    def get_children(self):
        return self._children

    def add_children(self, node):
        self._children.append(node)


class Tree:
    _nodes = []
    _edges = []

    def __init__(self):
        pass

    def add_node(self, node):
        self._nodes.append(node)

    def removeNode(self):
        pass

    def listChildren(self, url):
        pass

    def getParent(self, node):
        pass

    def getNodeLevel(self, node):
        pass
    def getTreeHeight(self):
        pass