from ArtisanPrint.custom_exceptions import ColorNotFound
from typing import Literal

COLORS = {
'olive':(128, 128, 0),
'crimson':(220, 20, 60),
'indian red':(205, 92, 92),
'mauve':(203, 78, 97),
'indigo':(75, 0, 130),
'snow':(255, 250, 250),
'ghost white':(248, 248, 255),
'white smoke':(245, 245, 245),
'gainsboro':(220, 220, 220),
'floral white':(255, 250, 240),
'old lace':(253, 245, 230),
'linen':(250, 240, 230),
'antique white':(250, 235, 215),
'papaya whip':(255, 239, 213),
'blanched almond':(255, 235, 205),
'bisque':(255, 228, 196),
'peach puff':(255, 218, 185),
'PeachPuff':(255, 218, 185),
'navajo white':(255, 222, 173),
'moccasin':(255, 228, 181),
'cornsilk':(255, 248, 220),
'ivory':(255, 255, 240),
'lemon chiffon':(255, 250, 205),
'seashell':(255, 245, 238),
'honeydew':(240, 255, 240),
'mint cream':(245, 255, 250),
'azure':(240, 255, 255),
'alice blue':(240, 248, 255),
'lavender':(230, 230, 250),
'lavender blush':(255, 240, 245),
'misty rose':(255, 228, 225),
'white':(255, 255, 255),
'black':(0, 0, 0),
'dark slate grey':(47, 79, 79),
'dim grey':(105, 105, 105),
'slate grey':(112, 128, 144),
'light slate grey':(119, 136, 153),
'grey':(190, 190, 190),
'light grey':(211, 211, 211),
'midnight blue':(25, 25, 112),
'navy':(0, 0, 128),
'navy blue':(0, 0, 128),
'cornflower blue':(100, 149, 237),
'dark slate blue':(72, 61, 139),
'slate blue':(106, 90, 205),
'medium slate blue':(123, 104, 238),
'light slate blue':(132, 112, 255),
'medium blue':(0, 0, 205),
'royal blue':(65, 105, 225),
'blue':(0, 0, 255),
'dodger blue':(30, 144, 255),
'deep sky blue':(0, 191, 255),
'sky blue':(135, 206, 235),
'light sky blue':(135, 206, 250),
'steel blue':(70, 130, 180),
'light steel blue':(176, 196, 222),
'light blue':(173, 216, 230),
'powder blue':(176, 224, 230),
'pale turquoise':(175, 238, 238),
'dark turquoise':(0, 206, 209),
'medium turquoise':(72, 209, 204),
'turquoise':(64, 224, 208),
'cyan':(0, 255, 255),
'light cyan':(224, 255, 255),
'cadet blue':(95, 158, 160),
'medium aquamarine':(102, 205, 170),
'aquamarine':(127, 255, 212),
'dark green':(0, 100, 0),
'dark olive green':(85, 107, 47),
'dark sea green':(143, 188, 143),
'sea green':(46, 139, 87),
'medium sea green':(60, 179, 113),
'light sea green':(32, 178, 170),
'pale green':(152, 251, 152),
'spring green':(0, 255, 127),
'lawn green':(124, 252, 0),
'green':(0, 255, 0),
'chartreuse':(127, 255, 0),
'medium spring green':(0, 250, 154),
'green yellow':(173, 255, 47),
'lime green':(50, 205, 50),
'yellow green':(154, 205, 50),
'forest green':(34, 139, 34),
'olive drab':(107, 142, 35),
'dark khaki':(189, 183, 107),
'khaki':(240, 230, 140),
'pale goldenrod':(238, 232, 170),
'light goldenrod yellow':(250, 250, 210),
'light yellow':(255, 255, 224),
'yellow':(255, 255, 0),
'gold':(255, 215, 0),
'light goldenrod':(238, 221, 130),
'goldenrod':(218, 165, 32),
'dark goldenrod':(184, 134, 11),
'rosy brown':(188, 143, 143),
'indian red':(205, 92, 92),
'saddle brown':(139, 69, 19),
'sienna':(160, 82, 45),
'peru':(205, 133, 63),
'burlywood':(222, 184, 135),
'beige':(245, 245, 220),
'wheat':(245, 222, 179),
'sandy brown':(244, 164, 96),
'tan':(210, 180, 140),
'chocolate':(210, 105, 30),
'fire brick':(178, 34, 34),
'brown':(165, 42, 42),
'dark salmon':(233, 150, 122),
'salmon':(250, 128, 114),
'light salmon':(255, 160, 122),
'orange':(255, 165, 0),
'dark orange':(255, 140, 0),
'coral':(255, 127, 80),
'light coral':(240, 128, 128),
'tomato':(255, 99, 71),
'orange red':(255, 69, 0),
'red':(255, 0, 0),
'hot pink':(255, 105, 180),
'deep pink':(255, 20, 147),
'pink':(255, 192, 203),
'light pink':(255, 182, 193),
'pale violet red':(219, 112, 147),
'maroon':(176, 48, 96),
'medium violet red':(199, 21, 133),
'violet red':(208, 32, 144),
'magenta':(255, 0, 255),
'violet':(238, 130, 238),
'plum':(221, 160, 221),
'orchid':(218, 112, 214),
'medium orchid':(186, 85, 211),
'dark orchid':(153, 50, 204),
'dark violet':(148, 0, 211),
'blue violet':(138, 43, 226),
'purple':(160, 32, 240),
'medium purple':(147, 112, 219),
'thistle':(216, 191, 216),
'dark grey':(169, 169, 169),
'dark blue':(0, 0, 139),
'dark cyan':(0, 139, 139),
'dark magenta':(139, 0, 139),
'dark red':(139, 0, 0),
'light green':(144, 238, 144),
}

text_styles = {
    'bold': '\033[1m',  # Bold text
    'faint': '\033[2m',  # Faint (decreased intensity) text
    'italic': '\033[3m',  # Italic text
    'underlined': '\033[4m',  # Underlined text
    'blinking': '\033[5m',  # Blinking text
    'inverted': '\033[7m',  # Inverted (swap foreground and background) text
    'hidden': '\033[8m',  # Hidden text (invisible)
}

def get_color_values_from_color(color:str)->tuple:
    if not isinstance(color, str):
        raise TypeError(f"Input color must be a 'str', not '{type(color).__name__}'")
     
    color = color.lower().strip()

    if color not in COLORS.keys():
        raise ColorNotFound(color)
    else:
        return COLORS[color]
    


def cprint(*values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file = None,
    flush: Literal[False] = False,
    color: str | tuple | None = None,
    bg_color: str | tuple | None = None,
    style: str | None = None,
    ) -> None:
    
    """
        Print text with optional text style, text color, and background color.

        
        Parameters:
        -----------

            *values (object) : Values to be printed.
            
            sep (str | None, optional) : Separator between values. Default is a space.
            
            end (str | None, optional) : String to print at the end. Default is a newline.
            
            file (object, optional) : File to write to. Default is None (stdout).
            
            flush (Literal[False], optional) : Whether to flush the output. Default is False.
            
            color (str | tuple(r,g,b) | None, optional) : Text color name or RGB tuple. Default is None.
            
            bg_color (str | tuple(r,g,b) | None, optional) : Background color name or RGB tuple. Default is None.
            
            style (str | None, optional) : Text style (e.g., 'bold', 'italic'). Default is None.

        Returns:
        --------
            None

        Notes:
        ------
            - ANSI escape codes are used for text formatting. The availability and behavior of these codes may vary depending on the terminal or console.
            - You can specify text color and background color either by using ANSI color codes (e.g., 'red' or (255, 0, 0)).
            - Text styles and color codes are case-insensitive.

        Example:
        --------
            - cprint("Hello, world!", color = "red", bg_color = "green", style = "bold")
            
            - cprint("Hello, world!", color = (255,0,0), bg_color = (0,255,0), style = "underlined")
        """
    if(file):
        print(*values, sep = sep, end = end, file = file, flush = flush)
        return
    
    text_color_code = ''
    bg_color_code = ''
    style_code = ''
    reset_code = '\033[0m'


    if color != None:
        if isinstance(color,str):
            r, g, b = get_color_values_from_color(color = color)
            text_color_code = f'\033[38;2;{r};{g};{b}m'
        elif isinstance(color,tuple):
            r, g, b = color
            text_color_code = f'\033[38;2;{r};{g};{b}m'
        else:
            raise TypeError(f"Input color must be a 'str' or 'tuple', not '{type(color).__name__}'")
    if bg_color != None:
        if isinstance(bg_color,str):
            r, g, b = get_color_values_from_color(color = bg_color)
            bg_color_code = f'\033[48;2;{r};{g};{b}m'
        elif isinstance(bg_color,tuple):
            r, g, b = bg_color
            bg_color_code = f'\033[48;2;{r};{g};{b}m'
        else:
            raise TypeError(f"Input bg_color must be a 'str' or 'tuple', not '{type(color).__name__}'")

    if style:
        style = style.lower().strip()
        if isinstance(style,str):
            if style in text_styles.keys():
                style_code = text_styles[style] 
            else:
                raise KeyError(f"Unknown style: {style}. Valid Styles are {text_styles.keys()}")
        else:
            raise TypeError(f"Invalid style type {type(style).__name__}({style})")
    
    print(text_color_code, bg_color_code, style_code, sep="", end = "")
    print(*values, reset_code, sep = sep, end = end, file = file, flush = flush)
