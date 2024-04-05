from PyCompGeomAlgorithms.core import Point
from PyCompGeomAlgorithms.quickhull import QuickhullNode, QuickhullTree, quickhull


def test_quickhull1():
    pts = [Point(3, 4), Point(0, 0), Point(7, 2)]
    hull = [pts[1], pts[0], pts[2]]
    tree = QuickhullTree(QuickhullNode([pts[1], pts[0], pts[2]], subhull=hull))
    tree.root.left = QuickhullNode([pts[1], pts[0], pts[2]], h=pts[0], subhull=hull)
    tree.root.right = QuickhullNode([pts[2], pts[1]], subhull=[pts[2], pts[1]])
    tree.root.left.left = QuickhullNode([pts[1], pts[0]], subhull=[pts[1], pts[0]])
    tree.root.left.right = QuickhullNode([pts[0], pts[2]], subhull=[pts[0], pts[2]])

    ans = quickhull(pts)
    lp, rp, s1, s2 = next(ans)
    
    assert (lp, rp) == (pts[1], pts[2])
    assert (s1, s2) == ([pts[1], pts[0], pts[2]], [pts[2], pts[1]])
    assert next(ans) == tree
    assert next(ans) == tree
    assert next(ans) == tree
    assert next(ans) == tree
    assert next(ans) == hull


def test_quickhull2():
    pts = [
        Point(0, 6),
        Point(8, 11),
        Point(10, 4),
        Point(7, 13),
        Point(6, 3),
        Point(3, 0),
        Point(4, 2),
        Point(12, 1),
        Point(14, 10),
        Point(5, 9),
        Point(3, 11),
        Point(1, 4),
    ]
    hull = [pts[0], pts[10], pts[3], pts[8], pts[7], pts[5]]
    tree = QuickhullTree(
        QuickhullNode(
            [
                pts[0],
                pts[10],
                pts[9],
                pts[3],
                pts[1],
                pts[8],
                pts[7],
                pts[2],
                pts[4],
                pts[6],
                pts[5],
                pts[11],
            ],
            subhull=hull
        )
    )

    tree.root.left = QuickhullNode(
        [pts[0], pts[10], pts[9], pts[3], pts[1], pts[8]],
        h=pts[3],
        subhull=[pts[0], pts[10], pts[3], pts[8]]
    )
    tree.root.right = QuickhullNode(
        [pts[8], pts[7], pts[2], pts[4], pts[6], pts[5], pts[11], pts[0]],
        h=pts[7],
        subhull=[pts[8], pts[7], pts[5], pts[0]]
    )

    tree.root.left.left = QuickhullNode([pts[0], pts[10], pts[3]], h=pts[10], subhull=[pts[0], pts[10], pts[3]])
    tree.root.left.right = QuickhullNode([pts[3], pts[8]], subhull=[pts[3], pts[8]])
    tree.root.left.left.left = QuickhullNode([pts[0], pts[10]], subhull=[pts[0], pts[10]])
    tree.root.left.left.right = QuickhullNode([pts[10], pts[3]], subhull=[pts[10], pts[3]])

    tree.root.right.left = QuickhullNode([pts[8], pts[7]], subhull=[pts[8], pts[7]])
    tree.root.right.right = QuickhullNode(
        [pts[7], pts[4], pts[6], pts[5], pts[11], pts[0]],
        h=pts[5],
        subhull=[pts[7], pts[5], pts[0]]
    )
    tree.root.right.right.left = QuickhullNode([pts[7], pts[5]], subhull=[pts[7], pts[5]])
    tree.root.right.right.right = QuickhullNode([pts[5], pts[0]], subhull=[pts[5], pts[0]])

    ans = quickhull(pts)
    lp, rp, s1, s2 = next(ans)

    assert (lp, rp) == (pts[0], pts[8])
    assert (s1, s2) == (tree.root.left.points, tree.root.right.points)
    assert next(ans) == tree
    assert next(ans) == tree
    assert next(ans) == tree
    assert next(ans) == tree
    assert next(ans) == hull
