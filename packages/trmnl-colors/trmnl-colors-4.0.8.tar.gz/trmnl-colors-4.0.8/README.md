# trmnl_colors v-4.0.8
## Add colors to the static WOrLd!

This module is made to colorize the output of terminal when the code runs on command line, With that there are functions for adding basic text colors (Total 10 including invisible) and or text formats such as Bold, Italics, Underline, Light or Strike-through to your code.

But wait there is more! use background colors, filled Variants which can be accessed by calling their specific name and 'Bg' postfix as in background. Here is an example describing with  use case:

```python
from trmnl_colors import *
blueBg()
print("Hello")
reset()
```

## Latest Updates:

### Introducing constants to make your life more easier:

>### Use case for constants

```python
from trmnl_colors.constants import *

print(RedBold + "Hello" + GreenBold + " World!", end="")

print(RESET,end="")

```
>### Use case for functions

```python
from trmnl_colors.functions import *
blueBg()
print("Hello")
white()
```

```python
from trmnl_colors.functions import *
yellowBold()
print("Hello") # After every color call remember to call the reset function.
# Outputs Hello in yellow color in Bold text
white()
```

* There are also filled color variants in which the font color and the background color match each other making them viable for specific type of color operations. 

* There is a special function called white() which is basically the default white so that the color function gets reset it is recommended to use this function at the end to maintain the color of the terminal.
* PS. if you want to create blocks of colors for decoration purposes use filled variants e.g. whiteFilled() 

## Terminal Application Screenshots with trmnl_colors:
### Create Terminal programs such as the below examples. Only your imagination and python skills are a limit!

![Screenshots](https://github.com/Idrisvohra9/trmnl-colors/blob/main/static/Screenshot%202023-08-24%20171908.png?raw=true)
![Screenshots](https://github.com/Idrisvohra9/trmnl-colors/blob/main/static/Screenshot%202023-08-24%20172610.png?raw=true)
> Explore & stay Creative

>## by: [Idris Vohra]("https://github.com/Idrisvohra9")
