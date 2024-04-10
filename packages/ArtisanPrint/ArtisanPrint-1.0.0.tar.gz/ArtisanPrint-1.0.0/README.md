# ArtisanPrint

ArtisanPrint is a Python library for printing text with customizable text styles, colors, and background colors. It provides a simple interface to enhance the appearance of printed text in the terminal.

## Installation

To install ArtisanPrint, simply use pip:

```bash
pip install ArtisanPrint
```

## Usage

Import the cprint function from the ArtisanPrint library and use it to print text with desired styles and colors.


## Examples

### Print Colored Text
```python
from artisanprint import cprint

cprint("Error: Something went wrong", color="red")
```

### Print Text with Background Color
```python
from artisanprint import cprint

cprint("Warning: Proceed with caution", bg_color="yellow")
```
### Print Text with Style
```python
from artisanprint import cprint

cprint("Important Message", style="bold")
```
### More Examples

```python

from ArtisanPrint import cprint

# Print text with red color and bold style
cprint("Hello, world!", color="red", style="bold")

# Print text with green background color and italic style
cprint("Welcome to ArtisanPrint", bg_color="green", style="italic")

# Print text with custom RGB color and underlined style
cprint("Custom Color", color=(255, 128, 0), style="underlined")

# Print text with multiple styles and background color
cprint("Formatted Text", style="bold italic", bg_color="blue")
```

## Notes

- ANSI escape codes are used for text formatting. The availability and behavior of these codes may vary depending on the terminal or console.
- You can specify text color and background color either by using color names or RGB tuples.
- Text styles and color codes are case-insensitive.