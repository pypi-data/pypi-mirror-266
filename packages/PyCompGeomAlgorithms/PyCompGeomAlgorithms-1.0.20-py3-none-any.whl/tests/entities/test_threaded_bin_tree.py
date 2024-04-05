from copy import deepcopy
from PyCompGeomAlgorithms.core import ThreadedBinTreeNode, ThreadedBinTree


def test_threaded_bin_trees_eq():
    f = root = ThreadedBinTreeNode("F")
    b = root.left = ThreadedBinTreeNode("B")
    a = root.left.left = ThreadedBinTreeNode("A")
    d = root.left.right = ThreadedBinTreeNode("D")
    c = root.left.right.left = ThreadedBinTreeNode("C")
    e = root.left.right.right = ThreadedBinTreeNode("E")
    g = root.right = ThreadedBinTreeNode("G")
    i = root.right.right = ThreadedBinTreeNode("I")
    h = root.right.right.left = ThreadedBinTreeNode("H")

    root2 = deepcopy(root)
    tree = ThreadedBinTree(root2)

    a.prev, a.next = i, b
    b.prev, b.next = a, c
    c.prev, c.next = b, d
    d.prev, d.next = c, e
    e.prev, e.next = d, f
    f.prev, f.next = e, g
    g.prev, g.next = f, h
    h.prev, h.next = g, i
    i.prev, i.next = h, a

    assert root == tree.root


def test_threaded_bin_tree_from_iterable():
    lst = ["A", "B", "C", "D", "E"]
    c = root = ThreadedBinTreeNode("C")
    a = root.left = ThreadedBinTreeNode("A")
    b = root.left.right = ThreadedBinTreeNode("B")
    d = root.right = ThreadedBinTreeNode("D")
    e = root.right.right = ThreadedBinTreeNode("E")

    a.prev, a.next = e, b
    b.prev, b.next = a, c
    c.prev, c.next = b, d
    d.prev, d.next = c, e
    e.prev, e.next = d, a

    tree = ThreadedBinTree(root)
    assert tree == ThreadedBinTree.from_iterable(lst)


def test_threaded_bin_tree_non_circular():
    b = root = ThreadedBinTreeNode("B")
    a = root.left = ThreadedBinTreeNode("A")
    c = root.right = ThreadedBinTreeNode("C")

    a.next = b
    b.prev, b.next = a, c
    c.prev = b
    
    tree = ThreadedBinTree(root)
    assert tree == ThreadedBinTree.from_iterable(["A", "B", "C"], circular=False)
