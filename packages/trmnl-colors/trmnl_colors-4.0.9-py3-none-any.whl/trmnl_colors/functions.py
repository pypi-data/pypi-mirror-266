"""
This code snippet defines a series of functions that print colored text in the console using ANSI escape codes. Each function corresponds to a different color or text style, such as bold, italics, underline, or strike-through. There are also functions for setting the background color and making the text invisible. The functions take no arguments and simply print the appropriate escape code to change the text color or style. The escape codes are represented as strings and are printed using the print() function with the end parameter set to an empty string to prevent a newline character from being added. The code snippet is not a class, but a collection of standalone functions.

Use Case:

```python
from trmnl_colors.functions import *
blueBg()
print("Hello")
white()
```

"""


def black():  # Default
    print("\033[0;30m", end="")


def blackBold():  # Bold
    print("\033[1;30m", end="")


def blackLight():  # Light
    print("\033[2;30m", end="")


def blackItalics():  # Italics
    print("\033[3;30m", end="")


def blackUnderline():  # Underline
    print("\033[4;30m", end="")


def blackStrikeThrough():  # StrikeThrough
    print("\033[9;30m", end="")

# Red:-


def red():  # Default
    print("\033[0;31m", end="")


def redBold():  # Bold
    print("\033[1;31m", end="")


def redLight():  # Light
    print("\033[2;31m", end="")


def redItalics():  # Italics
    print("\033[3;31m", end="")


def redUnderline():  # Underline
    print("\033[4;31m", end="")


def redStrikeThrough():  # StrikeThrough
    print("\033[9;31m", end="")


# Green:-
def green():
    print("\033[0;32m", end="")


def greenBold():
    print("\033[1;32m", end="")


def greenLight():
    print("\033[2;32m", end="")


def greenItalics():
    print("\033[3;32m", end="")


def greenUnderline():
    print("\033[4;32m", end="")


def greenStrikeThrough():
    print("\033[9;32m", end="")


# Yellow:-
def yellow():
    print("\033[0;33m", end="")


def yellowBold():
    print("\033[1;33m", end="")


def yellowLight():
    print("\033[2;33m", end="")


def yellowItalics():
    print("\033[3;33m", end="")


def yellowUnderline():
    print("\033[4;33m", end="")


def yellowStrikeThrough():
    print("\033[9;33m", end="")


# Blue:-
def blue():
    print("\033[0;34m", end="")


def blueBold():
    print("\033[1;34m", end="")


def blueLight():
    print("\033[2;34m", end="")


def blueItalics():
    print("\033[3;34m", end="")


def blueUnderline():
    print("\033[4;34m", end="")


def blueStrikeThrough():
    print("\033[9;34m", end="")


# Magenta:-
def magenta():
    print("\033[0;35m", end="")


def magentaBold():
    print("\033[1;35m", end="")


def magentaLight():
    print("\033[2;35m", end="")


def magentaItalics():
    print("\033[3;35m", end="")


def magentaUnderline():
    print("\033[4;35m", end="")


def magentaStrikeThrough():
    print("\033[9;35m", end="")


# Cyan:-
def cyan():
    print("\033[0;36m", end="")


def cyanBold():
    print("\033[1;36m", end="")


def cyanLight():
    print("\033[2;36m", end="")


def cyanItalics():
    print("\033[3;36m", end="")


def cyanUnderline():
    print("\033[4;36m", end="")


def cyanStrikeThrough():
    print("\033[9;36m", end="")

# Grey:-


def grey():
    print("\033[0;90m", end="")


def greyBold():
    print("\033[1;90m", end="")


def greyLight():
    print("\033[2;90m", end="")


def greyItalics():
    print("\033[3;90m", end="")


def greyUnderline():
    print("\033[4;90m", end="")


def greyStrikeThrough():
    print("\033[9;90m", end="")

# White:


def white():
    print("\033[0;0m", end='')


def whiteBold():
    print("\033[0;1m", end="")


def whiteLight():
    print("\033[0;2m", end="")


def whiteItalics():
    print("\033[0;3m", end="")


def whiteUnderline():
    print("\033[0;4m", end="")


def whiteStrikeThrough():
    print("\033[9;9m", end="")


# filled variant:
def redFilled():
    print("\033[31;41m", end='')


def yellowFilled():
    print("\033[33;43m", end='')


def greenFilled():
    print("\033[32;42m", end='')


def blueFilled():
    print("\033[34;44m", end='')


def magentaFilled():
    print("\033[35;45m", end='')


def cyanFilled():
    print("\033[36;46m", end='')


def whiteFilled():
    print("\033[37;47m", end='')


def blackFilled():
    print("\033[30;40m", end='')


def greyFilled():
    print("\033[90;100m", end='')

# Background:


def blackBg():
    print("\033[7;30m", end="")


def redBg():
    print("\033[7;31m", end="")


def greenBg():
    print("\033[7;32", end="")


def yellowBg():
    print("\033[7;33m", end="")


def blueBg():
    print("\033[7;34m", end="")


def magentaBg():
    print("\033[7;35m", end="")


def cyanBg():
    print("\033[7;36m", end="")


def whiteBg():
    print("\033[7;37m", end="")


def greyBg():
    print("\033[7;90m", end="")

# Invisible:


def invisible():
    print("\033[0;8m", end="")
