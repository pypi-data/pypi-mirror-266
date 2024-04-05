from .core import Point


def jarvis(points):
    if len(points) < 3:
        return sorted(points)
    
    index = points.index(min(points, key=lambda p: p.x))
    leftmost_index = index
    res = [points[index]]
    length = len(points)

    while True:
        next_index = (leftmost_index + 1) % length
        
        for i in range(length):
            if i != leftmost_index and direction_correct(points[leftmost_index], points[i], points[next_index]):
                next_index = i
        
        leftmost_index = next_index

        if leftmost_index == index:
            break

        res.append(points[next_index])
    
    return res


def direction_correct(point1, point2, point3):
    direction = Point.direction(point1, point2, point3)
    return (
        direction > 0 or
        direction == 0 and Point.dist(point1, point2) > Point.dist(point1, point3)
    )
