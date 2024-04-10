"""
You are building custom objects on which you would like to support iteration,
but would like an easy way to implement the iterator protocol.
"""


class Node:
    def __init__(self, value):
        self.value = value
        self._children = []

    def __repr__(self):
        return f"Node({self.value})"

    def add_child(self, node):
        self._children.append(node)

    def __iter__(self):
        return iter(self._children)

    def depth_first(self):
        yield self
        for child in self:
            yield from child.depth_first()


def main():
    root = Node(0)
    child1 = Node(1)
    child2 = Node(2)
    child3 = Node(3)
    root.add_child(child1)
    root.add_child(child2)
    root.add_child(child3)
    child1.add_child(Node(3))
    child2.add_child(Node(4))
    child3.add_child(Node(5))
    child3.add_child(Node(6))

    for child in root.depth_first():
        print(child)

    print(list(iter(root)))


if __name__ == "__main__":
    main()
