from math import pi
from .core import PyCGAObject, Point


class GrahamStepsTableRow(PyCGAObject):
    def __init__(self, point_triple, is_angle_less_than_pi):
        self.point_triple = point_triple
        self.is_angle_less_than_pi = is_angle_less_than_pi

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.point_triple == other.point_triple and
            self.is_angle_less_than_pi == other.is_angle_less_than_pi
        )
    
    def __str__(self):
        return f"[{str(self.point_triple)}, {str(self.is_angle_less_than_pi)}]"
    
    def __repr__(self):
        return str(self)


class GrahamStepsTable(PyCGAObject):
    def __init__(self, ordered_points, rows=None):
        super().__init__()
        self.ordered_points = ordered_points
        self.rows = rows if rows else []
    
    def append(self, item):
        self.rows.append(item)
    
    def extend(self, iterable):
        self.rows.extend(iterable)

    def __getitem__(self, key):
        return self.rows[key]
    
    def __setitem__(self, key, value):
        self.rows[key] = value

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.ordered_points == other.ordered_points and
            self.rows == other.rows
        )

    def __str__(self):
        return f"[{', '.join(str(row) for row in self)}]"
    
    def __repr__(self):
        return str(self)


def graham(points):
    if len(points) < 3:
        yield sorted(points, key=lambda p: (p.y, -p.x))
    else:
        i = 2
        while Point.direction(points[0], points[1], points[i]) == 0:
            i += 1
        
        centroid = Point.centroid(points[0], points[1], points[i])
        yield centroid

        origin = min(points, key=lambda p: (p.y, -p.x))
        ordered_points = sort_points(points, centroid, origin)
        yield ordered_points
        yield origin

        ordered_points.append(origin)
        steps_table = GrahamStepsTable(ordered_points)
        hull = make_hull(steps_table, ordered_points)
        ordered_points.pop()
        
        yield [row.point_triple for row in steps_table]
        yield [row.is_angle_less_than_pi for row in steps_table]
        yield steps_table
        yield steps_table
        yield steps_table
        
        yield hull


def sort_points(points, centroid, origin):
    min_angle = Point.polar_angle(origin, centroid)

    def angle_and_dist(p):
        p_angle = Point.polar_angle(p, centroid)
        angle = p_angle if p_angle >= min_angle else 2 * pi + p_angle
        return (angle, Point.dist(p, centroid))

    return sorted(points, key=angle_and_dist)


def make_hull(steps_table, ordered_points):
    res = ordered_points[:2]

    for point in ordered_points[2:]:
        while len(res) > 1 and Point.direction(res[-2], res[-1], point) >= 0:
            steps_table.append(GrahamStepsTableRow((res[-2], res[-1], point), False))
            res.pop()

        if len(res) > 1:
            steps_table.append(GrahamStepsTableRow((res[-2], res[-1], point), True))
        
        res.append(point)

    return res[:-1]
