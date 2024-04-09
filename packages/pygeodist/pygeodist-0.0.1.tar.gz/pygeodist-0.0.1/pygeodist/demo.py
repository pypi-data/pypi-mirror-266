from point import Point
from main import calculate_distance

point1 = Point(41.19,65.85)
point2 = Point(29.19,16.85)
print(calculate_distance(point1,point2))

point1 = Point(3,3)
point2 = Point(6,12)
print(calculate_distance(point1,point2, "m"))

print(calculate_distance(5,point2, "m"))
