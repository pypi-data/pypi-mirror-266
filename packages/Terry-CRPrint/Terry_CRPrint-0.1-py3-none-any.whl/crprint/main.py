"""
CRPrint - A module used for colorizing console output.

The CRPrint module provides functions to colorize the console output. It includes functions to validate colors, get color codes, print colored strings, and print colored lines.

- clear_color(func): A decorator which clears the console color after execution.

- colorize(color: tuple): Changes the color of the decorated function's output.

- get_color(color:tuple): Returns a code that can be used to change print color.

- color_print(text, color:tuple, print_value:bool=True, **kwargs): Prints a colored string. If `print_value` is `True`, it also prints the string without color.

- print_line(length:int, color:tuple=None, title:str=''): Prints a line of underscores with a specified length and a title. If `color` is not provided, it uses the default color.

- pretty_print(obj, indent=0, indent_increase=4, use_color=False, root=True, **kwargs): Prints an object neatly. If `use_color` is `True`, it also colors the string.
"""

indent_color_list = [
    (0, 150, 150),
    (0, 150, 70),
    (0, 200, 50),
    (100, 0, 0),
    (200, 200, 0),
]

def _validate_color(color):
    """
    Checks if passed color is a valid color.
    If the passed color is not a tuple, it tries to convert it to a tuple.
    If the color is not a list, it raises a TypeError.
    If the color has less than three values, it raises a ValueError.
    """
    if not type(color) == tuple:
        if type(color) == list:
            _validate_color(tuple(color))
        else:
            raise TypeError(f"{get_color((220, 0, 0))}Color must be a tuple, {type(color)} provided.\033[0m")
    elif len(color) < 3:
        raise ValueError(f"{get_color((250, 0, 0))}Color must have 3 values. Length: {len(color)}\033[0m")
    return color

def _get_whitespace(string):
    """Returns the amount of spaces before a given string"""
    return len(string) - len(string.lstrip())

def _wrap_number(num, limit, base=0):
    """
    Returns a number wrapped to a given limit.
    """
    if num > limit:
        return _wrap_number(num - (limit + base), limit, base)
    else:
        return num

def clear_color(func):
    """
    A decorator which clears the console color after execution.
    """
    def wrapper_clear_color(*args, **kwargs):
        func(*args, **kwargs)
        print("\033[0m\r", end='')
    return wrapper_clear_color

def colorize(color: tuple):
    """
    Changes the color of the decorated function's output.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            _validate_color(color)
            print(f'\033[38;2;{color[0]};{color[1]};{color[2]}m', end='')
            result = func(*args, **kwargs)
            print("\033[0m\r", end='')
            return result
        return wrapper
    return decorator

def get_color(color:tuple):
    """
    Returns a code that can be used to change print color.
    """
    color = _validate_color(color)
    return f'\033[38;2;{color[0]};{color[1]};{color[2]}m'

def color_print(text, color:tuple=(255,255,255), print_value:bool=True, **kwargs):
    """
    Prints a colored string.
    """
    color = _validate_color(color)
    output = f'\033[38;2;{color[0]};{color[1]};{color[2]}m{text}\033[0m'
    if print_value:
        print(f'\033[38;2;{color[0]};{color[1]};{color[2]}m{text}\033[0m', **kwargs)
    return output

def pretty_print(obj, indent=0, indent_increase=4, use_color=True, root=True, **kwargs):
    """
    Prints an object neatly.
    """
    return_string = ""

    if isinstance(obj, dict):
        # Display dict in "key: value" format
        for item in obj.items():
            return_string += "\n"
            val = pretty_print(item[1], indent + indent_increase, indent_increase, use_color, root=False, **kwargs)
            if not val.__contains__("\n"):
                val = val.lstrip()
            return_string += " "*indent + item[0] + ": " + val

    elif isinstance(obj, list) or isinstance(obj, tuple):
        # Display list in "index: value" format
        index = 0
        for item in obj:
            return_string += f"\n"

            val = pretty_print(item, indent + indent_increase, indent_increase, use_color, root=False, **kwargs)
            if not val.__contains__("\n"):
                val = val.lstrip(' ')
            else:
                val = "\n" + val

            return_string += " "*indent + f"{index}: " + val
            index += 1
        return_string = return_string.rstrip(",")

    else:
        return_string += " "*indent + str(obj)

    if root and use_color:
        # Colorize the string if it is the root function call
        colored_return = ""

        for x in return_string.split("\n"):
            colored_return += get_color(indent_color_list[_wrap_number(int(_get_whitespace(x)/4), len(indent_color_list)-1)]) + x + "\n"

        return colored_return.strip()

    return return_string.replace('\n\n', "\n")


@clear_color
def print_line(length:int, color:tuple=(255,255,255), title=''):
    """
    Prints a line of underscores with a specified length and a title.
    """
    color = _validate_color(color)
    print(get_color(color=color) + title + ''.join(['_' for x in range(length)]))

@clear_color
def demo():
    print_line(10)
    color_print("This is a demo of CRPrint.", (220, 220, 0))
    color_print("\nColored dictionary:", (220, 220, 0))
    print(pretty_print(
        {
        "Username": "John Doe",
        "Data": [
            {
            "Age": 37,
            "Tests": {
                "Ping": "Pong",
                "Pong": "Ping"
            }
            },
            ],
        "Connections": ("Billy Bob", "Jane Doe", "Guido van Rossum")
    }, 
    use_color=True
    ))


if __name__ == '__main__':
    demo()
