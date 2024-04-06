from PyCompGeomAlgorithms.core import BinTree, BinTreeNode


def test_bin_tree_height():
    tree = BinTree.from_iterable(i for i in range(1, 7))
    assert tree.root.height == 2
    assert tree.root.left.height == 1
    assert tree.root.left.right.height == 0
    assert tree.root.right.height == 1
    assert tree.root.right.left.height == 0
    assert tree.root.right.right.height == 0


class MockNode(BinTreeNode):
    def __init__(self, data, field, left=None, right=None, height=0):
        super().__init__(data, left, right, height)
        self.field = field


def test_bin_tree_node_copy_contents_without_children():
    root1 = MockNode("R1_2", 12, left=MockNode("R1_1", 11), right=MockNode("R1_3", 13))
    root2 = MockNode("R2_2", 22, left=MockNode("R2_1", 21), right=MockNode("R2_3", 23))
    MockNode.copy_contents_without_children(root1, root2)

    assert root2.data == "R1_2" and root2.field == 12
    assert root2.left.data == "R2_1" and root2.left.field == 21
    assert root2.right.data == "R2_3" and root2.right.field == 23


def test_bin_tree_node_copy_contents_without_children_same_node():
    root1 = MockNode("R1_2", 12, left=MockNode("R1_1", 11), right=MockNode("R1_3", 13))
    MockNode.copy_contents_without_children(root1, root1)

    assert root1.data == "R1_2" and root1.field == 12
    assert root1.left.data == "R1_1" and root1.left.field == 11
    assert root1.right.data == "R1_3" and root1.right.field == 13
