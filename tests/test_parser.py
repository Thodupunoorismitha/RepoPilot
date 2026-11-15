
from app.analyzer.parser import PythonCodeParser


def test_parser_extracts_functions_classes_and_imports():

    code = """
import os
from datetime import datetime

class Calculator:

    def add(self, a, b):
        return a + b

def greet(name):
    return "Hello " + name
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    assert [f["name"] for f in result["functions"]] == [
        "greet"
    ]

    assert [c["name"] for c in result["classes"]] == [
        "Calculator",
    ]
    
    assert [
        method["name"]
        for method in result["classes"][0]["methods"]
] == ["add"]

    assert result["imports"] == [
        "os",
        "datetime.datetime",
    ]


def test_parser_extracts_function_line_numbers():

    code = """def greet(name):
    return "Hello " + name
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    assert result["functions"] == [
        {
            "name": "greet",
            "parameters": ["name"],
            "calls": [],
            "start_line": 1,
            "end_line": 2,
        }
    ]

def test_parser_extracts_function_parameters():

    code = """def calculate(a, b, operation):
    return a + b
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    assert result["functions"][0]["parameters"] == [
        "a",
        "b",
        "operation",
    ]

def test_parser_extracts_class_inheritance():

    code = """
class Vehicle:
    pass

class Car(Vehicle):
    pass

class ElectricCar(Car):
    pass
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    assert result["classes"] == [
        {
            "name": "Vehicle",
            "bases": [],
	    "methods": [],
            "start_line": 2,
            "end_line": 3,
        },
        {
            "name": "Car",
            "bases": ["Vehicle"],
            "methods": [],
            "start_line": 5,
            "end_line": 6,
        },
        {
            "name": "ElectricCar",
            "bases": ["Car"],
            "methods": [],
            "start_line": 8,
            "end_line": 9,
        },
    ]

def test_parser_extracts_class_methods():

    code = """
class Calculator:

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    assert [
        method["name"]
        for method in result["classes"][0]["methods"]
] == [
    "add",
    "subtract",
]

def test_parser_separates_top_level_functions_from_methods():

    code = """
def greet():
    pass

class Calculator:
    def add(self, a, b):
        pass

def goodbye():
    pass
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    assert [f["name"] for f in result["functions"]] == [
        "greet",
        "goodbye",
    ]

    assert [
        method["name"]
        for method in result["classes"][0]["methods"]
] == ["add"]

def test_parser_extracts_function_calls():

    code = """
def calculate():
    pass

def main():
    calculate()
    print("Hello")
    calculate()
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    main_function = next(
        f for f in result["functions"]
        if f["name"] == "main"
    )

    assert main_function["calls"] == [
        "calculate",
        "print",
        "calculate",
    ]

def test_parser_extracts_attribute_calls():

    code = """
def main():
    calculator.add(10, 20)
    self.calculate()
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    main_function = next(
        f for f in result["functions"]
        if f["name"] == "main"
    )

    assert main_function["calls"] == [
        "calculator.add",
        "self.calculate",
    ]

def test_parser_extracts_method_calls():

    code = """
class Calculator:

    def add(self, a, b):
        return a + b

    def calculate(self):
        result = self.add(10, 20)
        print(result)
"""

    parser = PythonCodeParser()
    result = parser.parse(code)

    methods = result["classes"][0]["methods"]

    calculate_method = next(
        method for method in methods
        if method["name"] == "calculate"
    )

    assert calculate_method["calls"] == [
        "self.add",
        "print",
    ]