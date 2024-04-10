"""
You have built a custom container object that internally holds a list,
tuple or some other iterable. You would like to make iteration work
with your new container.
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


def main():
    root = Node(0)
    child1 = Node(1)
    child2 = Node(2)
    root.add_child(child1)
    root.add_child(child2)

    print(f"root node: {root}")

    for i, child in enumerate(root, 1):
        print(f"Child {i}: {child}")


if __name__ == "__main__":
    main()
