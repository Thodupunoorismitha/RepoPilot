
import math
import json
from pathlib import Path


class Shape:
    def area(self):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def describe(self):
        print("Circle area:", self.area())


def calculate_circle_area(radius):
    circle = Circle(radius)
    return circle.area()


def save_result(result, filename):
    data = {"area": result}

    with open(filename, "w") as file:
        json.dump(data, file)


def main():
    radius = 5
    area = calculate_circle_area(radius)
    save_result(area, "result.json")
    print("Calculation completed")


if __name__ == "__main__":
    main()
