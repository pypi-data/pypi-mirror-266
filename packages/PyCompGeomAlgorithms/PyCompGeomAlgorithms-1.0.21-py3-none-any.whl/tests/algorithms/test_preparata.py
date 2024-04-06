from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.preparata import preparata, PreparataThreadedBinTree


def test_preparata1():
    points = [Point(3, 2), Point(2, 4), Point(1, 1), Point(6, 2)]
    hull0 = [Point(1, 1), Point(2, 4), Point(3, 2)]
    hull = [Point(1, 1), Point(2, 4), Point(6, 2)]
    tree0 = PreparataThreadedBinTree.from_iterable(hull0)
    left_paths = [[Point(2, 4), Point(3, 2), Point(1, 1)]]
    right_paths = [[Point(2, 4)]]
    deleted_points = [[Point(3, 2)]]
    hulls = [hull]
    trees = []
    
    ans = preparata(points)
    assert next(ans) == (hull0, tree0)
    assert next(ans) == (left_paths, right_paths)
    assert next(ans) == deleted_points
    assert next(ans) == (hulls, trees)
    assert next(ans) == hull


def test_preparata2():
    # Corner case for convex (>--X) where one of the angles is equal to pi
    points = [Point(2, 2), Point(0, 1), Point(4, 3), Point(1, 0)]
    hull0 = [Point(0, 1), Point(2, 2), Point(1, 0)]
    hull = [Point(0, 1), Point(4, 3), Point(1, 0)]
    tree0 = PreparataThreadedBinTree.from_iterable(hull0)
    left_paths = [[Point(2, 2), Point(1, 0)]]
    right_paths = [[Point(2, 2), Point(0, 1)]]
    deleted_points = [[Point(2, 2)]]
    hulls = [hull]
    trees = []

    ans = preparata(points)
    assert next(ans) == (hull0, tree0)
    assert next(ans) == (left_paths, right_paths)
    assert next(ans) == deleted_points
    assert next(ans) == (hulls, trees)
    assert next(ans) == hull


def test_preparata3():
    # Corner case for convex (>--X) where one of the angles is equal to pi
    points = [Point(1, 2), Point(0, 0), Point(3, 0), Point(5, 0)]
    hull0 = [Point(0, 0), Point(1, 2), Point(3, 0)]
    hull = [Point(0, 0), Point(1, 2), Point(5, 0)]
    tree0 = PreparataThreadedBinTree.from_iterable(hull0)
    left_paths = [[Point(1, 2), Point(3, 0), Point(0, 0)]]
    right_paths = [[Point(1, 2)]]
    deleted_points = [[Point(3, 0)]]
    hulls = [hull]
    trees = []

    ans = preparata(points)
    assert next(ans) == (hull0, tree0)
    assert next(ans) == (left_paths, right_paths)
    assert next(ans) == deleted_points
    assert next(ans) == (hulls, trees)
    assert next(ans) == hull


def test_preparata4():
    # Corner cases for collinear first points and left and right supporting where one of the angles is 0
    points = [Point(1, 1), Point(1, 5), Point(5, 3), Point(1, 11), Point(6, 1), Point(10, 1)]
    hull0 = [Point(1, 1), Point(1, 5), Point(5, 3)]
    hull = [Point(1, 1), Point(1, 11), Point(10, 1)]
    tree0 = PreparataThreadedBinTree.from_iterable(hull0)
    left_paths = [
        [Point(1, 5), Point(5, 3)],
        [Point(1, 11), Point(5, 3), Point(1, 1)],
        [Point(1, 11), Point(6, 1), Point(1, 1)]
    ]
    right_paths = [
        [Point(1, 5), Point(1, 1)],
        [Point(1, 11)],
        [Point(1, 11)]
    ]
    deleted_points = [[Point(1, 5)], [Point(5, 3)], [Point(6, 1)]]
    hulls = [
        [Point(1, 1), Point(1, 11), Point(5, 3)],
        [Point(1, 1), Point(1, 11), Point(6, 1)],
        hull
    ]
    trees = [PreparataThreadedBinTree.from_iterable(hulls[0]), PreparataThreadedBinTree.from_iterable(hulls[1])]

    ans = preparata(points)
    assert next(ans) == (hull0, tree0)
    assert next(ans) == (left_paths, right_paths)
    assert next(ans) == deleted_points
    assert next(ans) == (hulls, trees)
    assert next(ans) == hull


def test_preparata5():
    p1 = Point(7, 0)
    p2 = Point(3, 3)
    p3 = Point(0, 0)
    p4 = Point(10, 8)
    p5 = Point(7, 9)
    points = [p1, p2, p3, p4, p5]
    hull0 = [p3, p2, p1]
    hull = [p3, p5, p4, p1]
    tree0 = PreparataThreadedBinTree.from_iterable(hull0)
    left_paths = [
        [p2, p1],
        [p5, p1],
    ]
    right_paths = [
        [p2, p3],
        [p5],
    ]
    deleted_points = [[p2], []]
    hulls = [
        [p3, p5, p1],
        hull
    ]
    trees = [PreparataThreadedBinTree.from_iterable(hulls[0])]

    ans = preparata(points)
    assert next(ans) == (hull0, tree0)
    assert next(ans) == (left_paths, right_paths)
    assert next(ans) == deleted_points
    assert next(ans) == (hulls, trees)
    assert next(ans) == hull