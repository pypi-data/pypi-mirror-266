from .core import Line2D, BinTreeNode, BinTree, Point


sort_left_to_right = lambda p: (p.x, -p.y)
sort_right_to_left = lambda p: (-p.x, p.y)


class QuickhullNode(BinTreeNode):
    def __init__(self, data, left=None, right=None, h=None, subhull=None):
        super().__init__(data, left, right)
        self.h = h
        self.subhull = subhull
    
    @property
    def points(self):
        return self.data
    
    @points.setter
    def points(self, value):
        self.data = value
    
    @points.deleter
    def points(self):
        del self.data


class QuickhullTree(BinTree):
    node_class = QuickhullNode


def quickhull(points):
    leftmost_point = min(points, key=lambda p: p.coords)
    rightmost_point = max(points, key=lambda p: p.coords)

    subset1 = make_subset(points, leftmost_point, rightmost_point, sort_key=sort_left_to_right)
    subset2 = make_subset(points, rightmost_point, leftmost_point, sort_key=sort_right_to_left)

    tree = QuickhullTree(QuickhullNode(subset1 + subset2[1:-1]))
    tree.root.left, tree.root.right = QuickhullNode(subset1), QuickhullNode(subset2)

    hull = (
        partition(subset1, leftmost_point, rightmost_point, tree.root.left) +
        partition(subset2, rightmost_point, leftmost_point, tree.root.right)[1:-1]
    )
    tree.root.subhull = hull

    yield leftmost_point, rightmost_point, subset1, subset2
    yield tree
    yield tree
    yield tree
    yield tree

    yield hull


def partition(points, left, right, node):
    if len(points) == 2:
        node.subhull = [left, right]
        return node.subhull

    lr_line = Line2D(left, right)
    pts = filter(lambda p: p != left and p != right, points)

    h = max(pts, key=lambda p: (Point.dist(p, lr_line), Point.angle(left, p, right)))
    s1 = left_points(points, left, h)
    s2 = left_points(points, h, right)

    node.h, node.left, node.right = h, QuickhullNode(s1), QuickhullNode(s2)
    node.subhull = partition(s1, left, h, node.left) + partition(s2, h, right, node.right)[1:]
    
    return node.subhull


def make_subset(points, left, right, sort_key):
    return sorted(left_points(points, left, right), key=sort_key)


def left_points(points, p1, p2):
    """Points p1, p2 and those at the left of the vector p1->p2."""
    return (
        [p1] +
        [p for p in points if Point.direction(p1, p2, p) < 0] +
        [p2]
    )
