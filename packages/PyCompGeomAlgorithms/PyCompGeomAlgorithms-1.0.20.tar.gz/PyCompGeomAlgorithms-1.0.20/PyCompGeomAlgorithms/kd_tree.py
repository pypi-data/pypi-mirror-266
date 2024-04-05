from .core import BinTreeNode, BinTree


class KDTree(BinTree):
    def __init__(self, root, x_range, y_range):
        super().__init__(root)
        self.x_range = x_range
        self.y_range = y_range
        self.partition = []
        self.search_list = []

    def build_tree(self, points, node, vertical=True):
        mid = len(points) // 2
        part = (points[mid], vertical)
        
        if all(p[0] != part[0] for p in self.partition):
            self.partition.append(part)

        if mid == 0:
            return

        if vertical:
            sort_key = lambda p: p.y
        else:
            sort_key = lambda p: p.x
        
        list_l = sorted(points[:mid], key=sort_key)
        list_r = sorted(points[-mid:], key=sort_key)
        left, right = list_l[mid // 2], list_r[mid // 2]

        node.left = BinTreeNode(left)
        if node.data != right:
            node.right = BinTreeNode(right)

        self.build_tree(list_l, node.left, not vertical)
        self.build_tree(list_r, node.right, not vertical)

    def region_search(self, node, vertical=True):
        if vertical:
            left, right, coord = self.x_range[0], self.x_range[1], node.data.x
        else:
            left, right, coord = self.y_range[0], self.y_range[1], node.data.y

        points = []
        to_add = self.point_in_region(node.data)

        if to_add:
            points.append(node.data)

        intersection = left <= coord <= right        
        self.search_list.append((node.data, to_add, intersection))

        if node.left and left < coord:
            points.extend(self.region_search(node.left, not vertical))
        if node.right and coord < right:
            points.extend(self.region_search(node.right, not vertical))

        return points

    def point_in_region(self, point):
        return (
            self.x_range[0] <= point.x
            and point.x <= self.x_range[1]
            and self.y_range[0] <= point.y
            and point.y <= self.y_range[1]
        )


def kd_tree(points, x_range, y_range):
    ordered_x = sorted(points)
    ordered_y = sorted(points, key=lambda p: (p.y, p.x))
    yield ordered_x, ordered_y

    root = BinTreeNode(ordered_x[len(ordered_x) // 2])
    tree = KDTree(root, x_range, y_range)
    tree.build_tree(ordered_x, root)
    yield tree.partition
    yield tree

    result = tree.region_search(root, vertical=True)
    yield tree.search_list
    yield result
