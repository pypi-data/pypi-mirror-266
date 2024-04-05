"""
This code snippet defines color and style constants using ANSI escape sequences for text formatting in the terminal. The constants include various colors, styles (bold, light, italics, underline, strikethrough), and background colors. There are also constants for resetting the text formatting and making it invisible. These constants can be used to add color and style to text output in the terminal.

Note: This code snippet is not a class, function, or method. It is a set of variable assignments.

Use case:
```python
from trmnl_colors.constants import *

print(RedB + "Hello" + GreenB + " World!", end="")

print(RESET,end="")

```
"""
# Color and Style Constants
Black = "\033[0;30m"
BlackBold = "\033[1;30m"
BlackLight = "\033[2;30m"
BlackItalics = "\033[3;30m"
BlackUnderline = "\033[4;30m"
BlackStrikeThrough = "\033[9;30m"

Red = "\033[0;31m"
RedBold = "\033[1;31m"
RedLight = "\033[2;31m"
RedItalics = "\033[3;31m"
RedUnderline = "\033[4;31m"
RedStrikeThrough = "\033[9;31m"

Green = "\033[0;32m"
GreenBold = "\033[1;32m"
GreenLight = "\033[2;32m"
GreenItalics = "\033[3;32m"
GreenUnderline = "\033[4;32m"
GreenStrikeThrough = "\033[9;32m"

Yellow = "\033[0;33m"
YellowBold = "\033[1;33m"
YellowLight = "\033[2;33m"
YellowItalics = "\033[3;33m"
YellowUnderline = "\033[4;33m"
YellowStrikeThrough = "\033[9;33m"

Blue = "\033[0;34m"
BlueBold = "\033[1;34m"
BlueLight = "\033[2;34m"
BlueItalics = "\033[3;34m"
BlueUnderline = "\033[4;34m"
BlueStrikeThrough = "\033[9;34m"

Magenta = "\033[0;35m"
MagentaBold = "\033[1;35m"
MagentaLight = "\033[2;35m"
MagentaItalics = "\033[3;35m"
MagentaUnderline = "\033[4;35m"
MagentaStrikeThrough = "\033[9;35m"

Cyan = "\033[0;36m"
CyanBold = "\033[1;36m"
CyanLight = "\033[2;36m"
CyanItalics = "\033[3;36m"
CyanUnderline = "\033[4;36m"
CyanStrikeThrough = "\033[9;36m"

Grey = "\033[0;90m"
GreyBold = "\033[1;90m"
GreyLight = "\033[2;90m"
GreyItalics = "\033[3;90m"
GreyUnderline = "\033[4;90m"
GreyStrikeThrough = "\033[9;90m"

White = "\033[0;0m"
WhiteBold = "\033[0;1m"
WhiteLight = "\033[0;2m"
WhiteItalics = "\033[0;3m"
WhiteUnderline = "\033[0;4m"
WhiteStrikeThrough = "\033[9;9m"

# Background Constants
BlackBg = "\033[7;30m"
RedBg = "\033[7;31m"
GreenBg = "\033[7;32m"
YellowBg = "\033[7;33m"
BlueBg = "\033[7;34m"
MagentaBg = "\033[7;35m"
CyanBg = "\033[7;36m"
WhiteBg = "\033[7;37m"
GreyBg = "\033[7;90m"

# Reset and Invisible Constants
RESET = "\033[0;0m"
INVISIBLE = "\033[0;8m"
