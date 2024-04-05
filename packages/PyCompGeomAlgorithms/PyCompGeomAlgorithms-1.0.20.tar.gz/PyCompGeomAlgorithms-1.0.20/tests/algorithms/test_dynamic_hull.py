from copy import deepcopy
from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.dynamic_hull import DynamicHullNode, SubhullThreadedBinTree, DynamicHullTree, PathDirection, upper_dynamic_hull, merge


def test_dynamic_hull1():
    p2, p1, p3 = Point(3, 3), Point(1, 1), Point(5, 0)
    pts = [p2, p1, p3]
    root = DynamicHullNode(p2, [p1, p2, p3], 1)
    root.left = DynamicHullNode(p1, [p1, p2])
    root.left.left = DynamicHullNode.leaf(p1)
    root.left.right = DynamicHullNode.leaf(p2)
    root.right = DynamicHullNode.leaf(p3)
    tree = DynamicHullTree(root)
    
    optimized_tree = deepcopy(tree)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.left.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.left.left.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.left.right.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.right.optimized_subhull = SubhullThreadedBinTree.empty()
    
    leaves = [root.left.left, root.left.right, root.right]
    path = [PathDirection.right]
    point_to_insert = Point(4, 3)
    hull = [p1, p2, point_to_insert, p3]

    ans = upper_dynamic_hull(pts, point_to_insert)

    assert leaves == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert optimized_tree == next(ans)
    assert path == next(ans)

    optimized_tree.root.subhull = SubhullThreadedBinTree.from_iterable(hull)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.right = DynamicHullNode(point_to_insert, [point_to_insert, p3])
    optimized_tree.root.right.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.right.left = DynamicHullNode.leaf(point_to_insert)
    optimized_tree.root.right.left.optimized_subhull = SubhullThreadedBinTree.empty()
    optimized_tree.root.right.right = DynamicHullNode.leaf(p3)
    optimized_tree.root.right.right.optimized_subhull = SubhullThreadedBinTree.empty()

    assert (optimized_tree, hull) == next(ans)
    assert hull == next(ans)


def test_dynamic_hull2():
    pts = p5, p9, p4, p2, p6, p8, p3, p10, p7, p1, p11 = [
        Point(3, 10),
        Point(6, 8),
        Point(3, 5),
        Point(2, 8),
        Point(4, 8),
        Point(5, 5),
        Point(3, 3),
        Point(7, 7),
        Point(5, 0),
        Point(0, 0),
        Point(10, 3)
    ]
    root = DynamicHullNode(p6, [p1, p2, p5, p9, p10, p11], 2)
    root.left = DynamicHullNode(p3, [p1, p2, p5, p6], 1)
    root.left.left = DynamicHullNode(p2, [p1, p2, p3], 1)
    root.left.left.left = DynamicHullNode(p1, [p1, p2])
    root.left.left.left.left = DynamicHullNode.leaf(p1)
    root.left.left.left.right = DynamicHullNode.leaf(p2)
    root.left.left.right = DynamicHullNode.leaf(p3)
    root.left.right = DynamicHullNode(p5, [p5, p6])
    root.left.right.left = DynamicHullNode(p4, [p5])
    root.left.right.left.left = DynamicHullNode.leaf(p4)
    root.left.right.left.right = DynamicHullNode.leaf(p5)
    root.left.right.right = DynamicHullNode.leaf(p6)
    root.right = DynamicHullNode(p9, [p8, p9, p10, p11], 1)
    root.right.left = DynamicHullNode(p8, [p8, p9])
    root.right.left.left = DynamicHullNode(p7, [p8])
    root.right.left.left.left = DynamicHullNode.leaf(p7)
    root.right.left.left.right = DynamicHullNode.leaf(p8)
    root.right.left.right = DynamicHullNode.leaf(p9)
    root.right.right = DynamicHullNode(p10, [p10, p11])
    root.right.right.left = DynamicHullNode.leaf(p10)
    root.right.right.right = DynamicHullNode.leaf(p11)
    tree = DynamicHullTree(root)

    optimized_tree = deepcopy(tree)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.left.optimized_subhull = SubhullThreadedBinTree.from_iterable([p6])
    optimized_tree.root.left.left.optimized_subhull = SubhullThreadedBinTree.from_iterable([p3])
    optimized_tree.root.left.right.left.left.optimized_subhull = SubhullThreadedBinTree.from_iterable([p4])
    optimized_tree.root.right.optimized_subhull = SubhullThreadedBinTree.from_iterable([p8])
    optimized_tree.root.right.left.left.left.optimized_subhull = SubhullThreadedBinTree.from_iterable([p7])

    leaves = tree.leaves_inorder()
    path = [PathDirection.left, PathDirection.right, PathDirection.left, PathDirection.right]
    point_to_delete = p5
    hull = [p1, p2, p9, p10, p11]

    ans = upper_dynamic_hull(pts, point_to_delete)

    assert leaves == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert optimized_tree == next(ans)
    assert path == next(ans)

    optimized_tree.root.subhull = SubhullThreadedBinTree.from_iterable([p1, p2, p9, p10, p11])
    optimized_tree.root.optimized_subhull = deepcopy(optimized_tree.root.subhull)
    optimized_tree.root.left_supporting_index = 1
    
    optimized_tree.root.left.subhull = SubhullThreadedBinTree.from_iterable([p1, p2, p6])
    optimized_tree.root.left.right.left.right = optimized_tree.root.left.right.right
    optimized_tree.root.left.right = optimized_tree.root.left.right.left
    optimized_tree.root.left.right.subhull = SubhullThreadedBinTree.from_iterable([p4, p6])
    optimized_tree.root.left.right.optimized_subhull = SubhullThreadedBinTree.from_iterable([p4])
    optimized_tree.root.left.right.left.optimized_subhull = SubhullThreadedBinTree.empty()

    assert (optimized_tree, hull) == next(ans)
    assert hull == next(ans)


def test_dynamic_hull3():
    """Vertical line, only upper point"""
    pts = p1, p2, p3, p4, p5 = [Point(0, i) for i in range(5)]
    root = DynamicHullNode(p3, [p5])
    root.left = DynamicHullNode(p2, [p3])
    root.left.left = DynamicHullNode(p1, [p2])
    root.left.left.left = DynamicHullNode.leaf(p1)
    root.left.left.right = DynamicHullNode.leaf(p2)
    root.left.right = DynamicHullNode.leaf(p3)
    root.right = DynamicHullNode(p4, [p5])
    root.right.left = DynamicHullNode.leaf(p4)
    root.right.right = DynamicHullNode.leaf(p5)
    tree = DynamicHullTree(root)

    optimized_tree = deepcopy(tree)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.left.optimized_subhull = optimized_tree.root.left.subhull
    optimized_tree.root.left.left.optimized_subhull = optimized_tree.root.left.left.subhull
    optimized_tree.root.left.left.left.optimized_subhull = optimized_tree.root.left.left.left.subhull
    optimized_tree.root.right.left.optimized_subhull = optimized_tree.root.right.left.subhull

    leaves = tree.leaves_inorder()
    path = [PathDirection.right] * 2
    point_to_insert = Point(0, 6)
    hull = [point_to_insert]

    ans = upper_dynamic_hull(pts, point_to_insert)

    assert leaves == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert optimized_tree == next(ans)
    assert path == next(ans)

    optimized_tree.root.subhull = SubhullThreadedBinTree.from_iterable([point_to_insert])
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.right.subhull = SubhullThreadedBinTree.from_iterable([point_to_insert])
    optimized_tree.root.right.right = DynamicHullNode(p5, [point_to_insert])
    optimized_tree.root.right.right.left = DynamicHullNode(p5, [p5])
    optimized_tree.root.right.right.left.optimized_subhull = optimized_tree.root.right.right.left.subhull
    optimized_tree.root.right.right.right = DynamicHullNode(point_to_insert, [point_to_insert])
    
    assert (optimized_tree, hull) == next(ans)
    assert hull == next(ans)


def test_dynamic_hull4():
    """Horizontal line, segment of only extreme left and right points"""
    pts = p1, p2, p3, p4, p5 = [Point(i, 0) for i in range(1, 6)]
    root = DynamicHullNode(p3, [p1, p5])
    root.left = DynamicHullNode(p2, [p1, p3])
    root.left.left = DynamicHullNode(p1, [p1, p2])
    root.left.left.left = DynamicHullNode.leaf(p1)
    root.left.left.right = DynamicHullNode.leaf(p2)
    root.left.right = DynamicHullNode.leaf(p3)
    root.right = DynamicHullNode(p4, [p4, p5])
    root.right.left = DynamicHullNode.leaf(p4)
    root.right.right = DynamicHullNode.leaf(p5)
    tree = DynamicHullTree(root)

    optimized_tree = deepcopy(tree)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull
    optimized_tree.root.left.optimized_subhull = SubhullThreadedBinTree.from_iterable([p3])
    optimized_tree.root.left.left.optimized_subhull = SubhullThreadedBinTree.from_iterable([p2])
    optimized_tree.root.right.optimized_subhull = SubhullThreadedBinTree.from_iterable([p4])

    leaves = tree.leaves_inorder()
    path = [PathDirection.left] * 3
    point_to_insert = Point(0, 0)
    hull = [point_to_insert, p5]

    ans = upper_dynamic_hull(pts, point_to_insert)

    assert leaves == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert tree == next(ans)
    assert optimized_tree == next(ans)
    assert path == next(ans)

    optimized_tree.root.subhull = SubhullThreadedBinTree.from_iterable(hull)
    optimized_tree.root.optimized_subhull = optimized_tree.root.subhull

    optimized_tree.root.left = DynamicHullNode(p1, [point_to_insert, p3], optimized_subhull_points=[p3])
    optimized_tree.root.left.left = DynamicHullNode(point_to_insert, [point_to_insert, p1], optimized_subhull_points=[p1])
    optimized_tree.root.left.left.left = DynamicHullNode.leaf(point_to_insert)
    optimized_tree.root.left.left.right = DynamicHullNode.leaf(p1)
    optimized_tree.root.left.right = DynamicHullNode(p2, [p2, p3], optimized_subhull_points=[p2])
    optimized_tree.root.left.right.left = DynamicHullNode.leaf(p2)
    optimized_tree.root.left.right.right = DynamicHullNode.leaf(p3)

    assert (optimized_tree, hull) == next(ans)
    assert hull == next(ans)


def make_two_segment_nodes(points):
    p1, p2, p3, p4 = points
    n1, n2, n3, n4 = [DynamicHullNode.leaf(p) for p in points]

    segment_node1 = DynamicHullNode(p1, [p1, p2])
    segment_node1.left, segment_node1.right = n1, n2
    segment_node2 = DynamicHullNode(p3, [p3, p4])
    segment_node2.left, segment_node2.right = n3, n4
    
    return segment_node1, segment_node2


def test_merge_segments1():
    """Hull is p1-p4"""
    pts = [Point(0, 2), Point(1, 0), Point(3, 1), Point(4, 3)]
    p1, p2, p3, p4 = pts

    segment_node1, segment_node2 = make_two_segment_nodes(pts)
    joint_node = DynamicHullNode(p2, [p1, p4])
    joint_node.left, joint_node.right = segment_node1, segment_node2

    assert joint_node == merge(segment_node1, segment_node2)


def test_merge_segments2():
    """Hull is p1-p2-p4, p3 is below p1-p4"""
    pts = [Point(1, 1), Point(2, 4), Point(3, 1), Point(4, 2)]
    p1, p2, p3, p4 = pts

    segment_node1, segment_node2 = make_two_segment_nodes(pts)
    joint_node = DynamicHullNode(p2, [p1, p2, p4], 1)
    joint_node.left, joint_node.right = segment_node1, segment_node2

    assert joint_node == merge(segment_node1, segment_node2)


def test_merge_segments3():
    """Hull is p1-p2-p4, p3 is above p1-p4"""
    pts = [Point(1, 1), Point(2, 4), Point(3, 2), Point(4, 2)]
    p1, p2, p3, p4 = pts

    segment_node1, segment_node2 = make_two_segment_nodes(pts)
    joint_node = DynamicHullNode(p2, [p1, p2, p4], 1)
    joint_node.left, joint_node.right = segment_node1, segment_node2

    assert joint_node == merge(segment_node1, segment_node2)


def test_merge_segments4():
    """Hull is p1-p3-p4, p2 is below p1-p4"""
    pts = [Point(1, 3), Point(2, 1), Point(3, 3), Point(4, 1)]
    p1, p2, p3, p4 = pts

    segment_node1, segment_node2 = make_two_segment_nodes(pts)
    joint_node = DynamicHullNode(p2, [p1, p3, p4])
    joint_node.left, joint_node.right = segment_node1, segment_node2

    assert joint_node == merge(segment_node1, segment_node2)


def test_merge_segments5():
    """Hull is p1-p3-p4, p2 is above p1-p4"""
    pts = [Point(1, 3), Point(2, 3), Point(3, 4), Point(4, 1)]
    p1, p2, p3, p4 = pts

    segment_node1, segment_node2 = make_two_segment_nodes(pts)
    joint_node = DynamicHullNode(p2, [p1, p3, p4])
    joint_node.left, joint_node.right = segment_node1, segment_node2

    assert joint_node == merge(segment_node1, segment_node2)


def test_merge_segments6():
    """Hull is p1-p2-p3-p4"""
    pts = [Point(1, 1), Point(2, 3), Point(3, 3), Point(4, 1)]
    p1, p2, p3, p4 = pts

    segment_node1, segment_node2 = make_two_segment_nodes(pts)
    joint_node = DynamicHullNode(p2, [p1, p2, p3, p4], 1)
    joint_node.left, joint_node.right = segment_node1, segment_node2

    assert joint_node == merge(segment_node1, segment_node2)


def test_merge_segment_and_point1():
    """Segment p1-p2 and point p3, where p2 is above p1-p3."""
    pts = [Point(0, 1), Point(2, 0), Point(5, 5)]
    p1, p2, p3 = pts
    n1, n2, n3 = [DynamicHullNode.leaf(p) for p in pts]
    segment_node = DynamicHullNode(p1, [p1, p2])
    segment_node.left, segment_node.right = n1, n2
    point_node = DynamicHullNode(p3, [p3])

    joint_node = DynamicHullNode(p2, [p1, p3])
    joint_node.left, joint_node.right = segment_node, n3

    assert joint_node == merge(segment_node, point_node)


def test_merge_segment_and_point2():
    """Segment p1-p2 and point p3, where p2 is above p1-p3."""
    pts = [Point(0, 1), Point(2, 3), Point(5, 0)]
    p1, p2, p3 = pts
    n1, n2, n3 = [DynamicHullNode.leaf(p) for p in pts]
    segment_node = DynamicHullNode(p1, [p1, p2])
    segment_node.left, segment_node.right = n1, n2
    point_node = DynamicHullNode(p3, [p3])

    joint_node = DynamicHullNode(p2, [p1, p2, p3], 1)
    joint_node.left, joint_node.right = segment_node, n3

    assert joint_node == merge(segment_node, point_node)
