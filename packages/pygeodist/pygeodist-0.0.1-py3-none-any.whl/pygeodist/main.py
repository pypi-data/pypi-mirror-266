import math
from geodistance.point import Point

def calculate_distance(pointA: Point, pointB: Point, unit: str = "km", result_decimal: int = 4):

    if type(pointA) == Point and type(pointB) == Point:

        if unit == "m":
            EARTH_RADIUS = 6371 * 1000
        else:
            EARTH_RADIUS = 6371

        dLat = math.radians(pointB.latitude - pointA.latitude)
        dLng = math.radians(pointB.longitude - pointA.longitude)

        a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
            math.cos(math.radians(pointA.latitude)) * \
            math.cos(math.radians(pointB.latitude)) * \
            math.sin(dLng / 2) * math.sin(dLng / 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return round(number = EARTH_RADIUS * c, ndigits = result_decimal)

    else:
        print("Invalid input value")
