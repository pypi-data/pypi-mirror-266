from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.jarvis import jarvis


def test_jarvis1():
    pts = [
        Point(1, 4),
        Point(0, 0),
        Point(3, 3),
        Point(3, 1),
        Point(7, 0),
        Point(5, 5),
        Point(5, 2),
        Point(9, 6),
    ]
    hull = [Point(0, 0), Point(1, 4), Point(9, 6), Point(7, 0)]

    ans = jarvis(pts)
    assert ans == hull


def test_jarvis2():
    pts = [Point(3, 3), Point(1, 1), Point(5, 0)]
    hull = [Point(1, 1), Point(3, 3), Point(5, 0)]

    ans = jarvis(pts)
    assert ans == hull
