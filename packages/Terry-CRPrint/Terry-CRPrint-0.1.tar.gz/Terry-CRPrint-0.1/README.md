CRPrint
-
A basic module used for colorizing console output.

The CRPrint module provides functions to colorize the console output. It includes functions to get color codes, print colored strings, and print colored lines.

- clear_color(func): A decorator which clears the console color after execution.

- colorize(color: tuple): A decorator which changes the color of the decorated function's output.

- get_color(color:tuple): Returns a code that can be used to change print color.

- color_print(text, color:tuple, print_value:bool=True, **kwargs): Prints a colored string. If `print_value` is `True`, it also prints the string without color.

- print_line(length:int, color:tuple=None, title:str=''): Prints a line of underscores with a specified length and a title. If `color` is not provided, it uses the default color.

- pretty_print(obj, indent=0, indent_increase=4, use_color=False, root=True, **kwargs): Prints an object neatly. If `use_color` is `True`, it also colors the string.
