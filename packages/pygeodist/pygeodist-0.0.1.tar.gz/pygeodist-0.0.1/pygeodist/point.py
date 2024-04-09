class Point():
    def __init__(self, latitude, longitude) -> None:

        try:
            self.latitude = latitude
            self.longitude = longitude

            if type(latitude) != float:
                self.latitude = float(latitude)

            if type(longitude) != float:
                self.longitude = float(longitude)

        except ValueError:
            print("Unable to convert.")
            self.latitude = 0.0
            self.longitude = 0.0

    def printPoints(self):
        print([self.latitude, self.longitude])