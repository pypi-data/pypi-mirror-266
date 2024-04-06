from copy import deepcopy
from PyCompGeomAlgorithms.core import BinTreeNode, AVLTree

def test_avl_tree_insertion_no_imbalance():
    test_tree = AVLTree.from_iterable(i for i in range(1, 6))
    tree = deepcopy(test_tree)

    test_tree.insert(6)
    tree.root.right.right.right = BinTreeNode(6)

    assert tree == test_tree


def test_avl_tree_deletion_no_imbalance():
    test_tree = AVLTree.from_iterable(i for i in range(1, 12))
    tree = deepcopy(test_tree)
    
    test_tree.delete(6)

    tree.root.data = 7
    tree.root.right.left = BinTreeNode(8)

    assert tree == test_tree


def test_avl_tree_insertion_left_left():
    test_tree = AVLTree.from_iterable(i for i in range(1, 8))
    test_tree.insert(3.5)
    test_tree.insert(1.25)
    test_tree.insert(1.5)

    root = BinTreeNode(2)
    root.left = BinTreeNode(1)
    root.left.right = BinTreeNode(1.25)
    root.left.right.right = BinTreeNode(1.5)
    root.right = BinTreeNode(4)
    root.right.left = BinTreeNode(3)
    root.right.left.right = BinTreeNode(3.5)
    root.right.right = BinTreeNode(6)
    root.right.right.left = BinTreeNode(5)
    root.right.right.right = BinTreeNode(7)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_insertion_right_right():
    test_tree = AVLTree.from_iterable(i for i in range(1, 8))
    test_tree.insert(5.5)
    test_tree.insert(8)
    test_tree.insert(9)

    root = BinTreeNode(6)
    root.left = BinTreeNode(4)
    root.left.left = BinTreeNode(2)
    root.left.left.left = BinTreeNode(1)
    root.left.left.right = BinTreeNode(3)
    root.left.right = BinTreeNode(5)
    root.left.right.right = BinTreeNode(5.5)
    root.right = BinTreeNode(7)
    root.right.right = BinTreeNode(8)
    root.right.right.right = BinTreeNode(9)
    tree = AVLTree(root)

    assert tree == test_tree

def test_avl_tree_insertion_left_right():
    test_tree = AVLTree.from_iterable(i for i in range(1, 12))
    test_tree.insert(0)
    test_tree.insert(0.5)
    test_tree.insert(3.25)
    test_tree.insert(3.5)
    test_tree.insert(5.25)
    test_tree.insert(5.5)
    
    root = BinTreeNode(4)
    root.left = BinTreeNode(3)
    root.left.left = BinTreeNode(1)
    root.left.left.left = BinTreeNode(0)
    root.left.left.left.right = BinTreeNode(0.5)
    root.left.left.right = BinTreeNode(2)
    root.left.right = BinTreeNode(3.25)
    root.left.right.right = BinTreeNode(3.5)
    root.right = BinTreeNode(6)
    root.right.left = BinTreeNode(5)
    root.right.left.right = BinTreeNode(5.25)
    root.right.left.right.right = BinTreeNode(5.5)
    root.right.right = BinTreeNode(9)
    root.right.right.left = BinTreeNode(7)
    root.right.right.left.right = BinTreeNode(8)
    root.right.right.right = BinTreeNode(10)
    root.right.right.right.right = BinTreeNode(11)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_insertion_right_left():
    test_tree = AVLTree.from_iterable(i for i in range(1, 12))
    test_tree.insert(6.25)
    test_tree.insert(6.5)
    test_tree.insert(8.25)
    test_tree.insert(12)
    test_tree.insert(8.5)

    root = BinTreeNode(7)
    root.left = BinTreeNode(6)
    root.left.left = BinTreeNode(3)
    root.left.left.left = BinTreeNode(1)
    root.left.left.left.right = BinTreeNode(2)
    root.left.left.right = BinTreeNode(4)
    root.left.left.right.right = BinTreeNode(5)
    root.left.right = BinTreeNode(6.25)
    root.left.right.right = BinTreeNode(6.5)
    root.right = BinTreeNode(9)
    root.right.left = BinTreeNode(8)
    root.right.left.right = BinTreeNode(8.25)
    root.right.left.right.right = BinTreeNode(8.5)
    root.right.right = BinTreeNode(10)
    root.right.right.right = BinTreeNode(11)
    root.right.right.right.right = BinTreeNode(12)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_deletion_left_left():
    test_tree = AVLTree.from_iterable(i for i in range(1, 8))
    test_tree.insert(1.5)
    test_tree.insert(3.5)
    test_tree.delete(5)
    test_tree.delete(7)

    root = BinTreeNode(2)
    root.left = BinTreeNode(1)
    root.left.right = BinTreeNode(1.5)
    root.right = BinTreeNode(4)
    root.right.left = BinTreeNode(3)
    root.right.left.right = BinTreeNode(3.5)
    root.right.right = BinTreeNode(6)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_deletion_right_right():
    test_tree = AVLTree.from_iterable(i for i in range(1, 8))
    test_tree.insert(5.5)
    test_tree.insert(8)
    test_tree.delete(1)
    test_tree.delete(2)

    root = BinTreeNode(6)
    root.left = BinTreeNode(4)
    root.left.left = BinTreeNode(3)
    root.left.right = BinTreeNode(5)
    root.left.right.right = BinTreeNode(5.5)
    root.right = BinTreeNode(7)
    root.right.right = BinTreeNode(8)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_deletiion_left_right():
    test_tree = AVLTree.from_iterable(i for i in range(1, 12))
    test_tree.insert(0)
    test_tree.insert(0.5)
    test_tree.insert(3.25)
    test_tree.insert(3.5)
    test_tree.insert(5.25)
    test_tree.insert(8.5)
    test_tree.insert(5.5)
    test_tree.delete(8.5)

    root = BinTreeNode(4)
    root.left = BinTreeNode(3)
    root.left.left = BinTreeNode(1)
    root.left.left.left = BinTreeNode(0)
    root.left.left.left.right = BinTreeNode(0.5)
    root.left.left.right = BinTreeNode(2)
    root.left.right = BinTreeNode(3.25)
    root.left.right.right = BinTreeNode(3.5)
    root.right = BinTreeNode(6)
    root.right.left = BinTreeNode(5)
    root.right.left.right = BinTreeNode(5.25)
    root.right.left.right.right = BinTreeNode(5.5)
    root.right.right = BinTreeNode(9)
    root.right.right.left = BinTreeNode(7)
    root.right.right.left.right = BinTreeNode(8)
    root.right.right.right = BinTreeNode(10)
    root.right.right.right.right = BinTreeNode(11)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_deletion_right_left():
    test_tree = AVLTree.from_iterable(i for i in range(1, 12))
    test_tree.insert(2.5)
    test_tree.insert(6.25)
    test_tree.insert(6.5)
    test_tree.insert(8.25)
    test_tree.insert(12)
    test_tree.insert(8.5)
    test_tree.delete(2.5)

    root = BinTreeNode(7)
    root.left = BinTreeNode(6)
    root.left.left = BinTreeNode(3)
    root.left.left.left = BinTreeNode(1)
    root.left.left.left.right = BinTreeNode(2)
    root.left.left.right = BinTreeNode(4)
    root.left.left.right.right = BinTreeNode(5)
    root.left.right = BinTreeNode(6.25)
    root.left.right.right = BinTreeNode(6.5)
    root.right = BinTreeNode(9)
    root.right.left = BinTreeNode(8)
    root.right.left.right = BinTreeNode(8.25)
    root.right.left.right.right = BinTreeNode(8.5)
    root.right.right = BinTreeNode(10)
    root.right.right.right = BinTreeNode(11)
    root.right.right.right.right = BinTreeNode(12)
    tree = AVLTree(root)

    assert tree == test_tree


def test_avl_tree_insertion_of_prefilled_node():
    test_tree = AVLTree.from_iterable(i for i in range(1, 3))
    test_tree.insert(BinTreeNode(0))

    tree = AVLTree(BinTreeNode(1, BinTreeNode(0), BinTreeNode(2)))
    assert tree == test_tree