from PyCompGeomAlgorithms.core import Point, BinTreeNode
from PyCompGeomAlgorithms.kd_tree import KDTree, kd_tree


def test_kd_tree():
    pts = [
        Point(0, 9),
        Point(2, 3),
        Point(3, 6),
        Point(5, 8),
        Point(6, 1),
        Point(8, 13),
        Point(10, 2),
        Point(12, 4),
        Point(14, 11),
        Point(15, 5),
        Point(17, 10)
    ]
    rx = [3, 14]
    ry = [0, 8]

    ordered_x = pts
    ordered_y = [
        Point(6, 1),
        Point(10, 2),
        Point(2, 3),
        Point(12, 4),
        Point(15, 5),
        Point(3, 6),
        Point(5, 8),
        Point(0, 9),
        Point(17, 10),
        Point(14, 11),
        Point(8, 13)
    ]

    tree = KDTree(BinTreeNode(Point(8, 13)), [], [])
    tree.root.left = BinTreeNode(Point(3, 6))
    tree.root.left.left = BinTreeNode(Point(6, 1))
    tree.root.left.left.left = BinTreeNode(Point(2, 3))
    tree.root.left.right = BinTreeNode(Point(5, 8))
    tree.root.left.right.left = BinTreeNode(Point(0, 9))

    tree.root.right = BinTreeNode(Point(15, 5))
    tree.root.right.left = BinTreeNode(Point(12, 4))
    tree.root.right.left.left = BinTreeNode(Point(10, 2))
    tree.root.right.right = BinTreeNode(Point(17, 10))
    tree.root.right.right.left = BinTreeNode(Point(14, 11))

    partition = [
        (Point(8, 13), True),
        (Point(3, 6), False),
        (Point(6, 1), True),
        (Point(2, 3), False),
        (Point(5, 8), True),
        (Point(0, 9), False),
        (Point(15, 5), False),
        (Point(12, 4), True),
        (Point(10, 2), False),
        (Point(17, 10), True),
        (Point(14, 11), False)
    ]

    search_list = [
        (Point(8, 13), False, True),
        (Point(3, 6), True, True),
        (Point(6, 1), True, True),
        (Point(2, 3), False, True),
        (Point(5, 8), True, True),
        (Point(0, 9), False, False),
        (Point(15, 5), False, True),
        (Point(12, 4), True, True),
        (Point(10, 2), True, True),
        (Point(17, 10), False, False),
        (Point(14, 11), False, False)
    ]

    result = [
        Point(3, 6),
        Point(5, 8),
        Point(6, 1),
        Point(10, 2),
        Point(12, 4),
    ]

    ans = kd_tree(pts, rx, ry)
    assert next(ans) == (ordered_x, ordered_y)
    assert next(ans) == partition
    assert next(ans) == tree
    assert next(ans) == search_list
    assert sorted(next(ans)) == result
