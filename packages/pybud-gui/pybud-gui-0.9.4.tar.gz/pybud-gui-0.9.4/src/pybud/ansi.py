
import os
import re
import string
from enum import Enum
from sys import stdin, stdout

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def InitAnsi():
    # call os.system("") to active ansi colors on the windows terminal
    os.system("")

# write and flash on stdout

f = stdout#open("output.ansi", "w", encoding="utf-8")

def write(data): f.write(data)
def writeln(data): f.write(data+"\n")
def read(): stdin.read()
def readln(): stdin.readline()
def flush(): f.flush()
        
# ansi colors
class ForeColors():
    Black          = "\x1B[0;30m"
    Red            = "\x1B[0;31m"
    Green          = "\x1B[0;32m"
    Yellow         = "\x1B[0;33m"
    Blue           = "\x1B[0;34m"
    Magenta        = "\x1B[0;35m"
    Cyan           = "\x1B[0;36m"
    White          = "\x1B[0;37m"

    Default        = "\x1B[0;39m"

    Dark_Gray      = "\x1B[1;30m"
    Light_Red      = "\x1B[1;31m"
    Light_Green    = "\x1B[1;32m"
    Light_Yellow   = "\x1B[1;33m"
    Light_Blue     = "\x1B[1;34m"
    Light_Magenta  = "\x1B[1;35m"
    Light_Cyan     = "\x1B[1;36m"
    Dimm_White     = "\x1B[1;37m"

    Light_Black = Dark_Gray
    Light_White = Dimm_White

class BackColors:
    Black          = "\x1B[0;40m"
    Red            = "\x1B[0;41m"
    Green          = "\x1B[0;42m"
    Yellow         = "\x1B[0;43m"
    Blue           = "\x1B[0;44m"
    Magenta        = "\x1B[0;45m"
    Cyan           = "\x1B[0;46m"
    White          = "\x1B[0;47m"

    Default        = "\x1B[0;49m"

    Dark_Gray      = "\x1B[1;40m"
    Light_Red      = "\x1B[1;41m"
    Light_Green    = "\x1B[1;42m"
    Light_Yellow   = "\x1B[1;43m"
    Light_Blue     = "\x1B[1;44m"
    Light_Magenta  = "\x1B[1;45m"
    Light_Cyan     = "\x1B[1;46m"
    Dimm_White     = "\x1B[1;47m"

    Light_Black = Dark_Gray
    Light_Gray = Dimm_White


class ColorType(Enum):
    C816COLOR = 1
    LEGACY = 2
    TRUECOLOR = 3

class AnsiColor():
    def __init__(self, rgb: tuple[int, int, int], foreground: bool = True):
        self.rgb = rgb
        self.foreground = foreground

    def __str__(self) -> str:
        return self.rgb

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return (self.rgb == other.rgb) and self.foreground == other.foreground

    # def __add__(self, other) -> str:
    #    return self.__str__() + other.__str__()

    @staticmethod
    def get_c816color_from_rgb(rgb: tuple[int, int, int], foreground: bool) -> str:
        raise NotImplementedError()

    @staticmethod
    def get_legacycolor_from_rgb(rgb: tuple[int, int, int], foreground: bool) -> str:
        if foreground:
            return FRgbAnsi(*rgb)
        else:
            return BRgbAnsi(*rgb)

    @staticmethod
    def get_truecolor_from_rgb(rgb: tuple[int, int, int], foreground: bool) -> str:
        if foreground:
            return FRgbAnsiTC(*rgb)
        else:
            return BRgbAnsiTC(*rgb)

    def get(self, ctype: ColorType = None) -> str:
        if ctype is None:
            ctype = ColorType.LEGACY

        if ctype == ColorType.C816COLOR:
            return self.get_c816color_from_rgb(self.rgb, self.foreground)
        elif ctype == ColorType.LEGACY:
            return self.get_legacycolor_from_rgb(self.rgb, self.foreground)
        elif ctype == ColorType.TRUECOLOR:
            return self.get_truecolor_from_rgb(self.rgb, self.foreground)

def remove_ansi(text):
    return ansi_escape.sub('', text)

def FRgbAnsiTC(R: int, G: int, B: int) -> string:
    return (f"\x1b[38;2;{R};{G};{B}m")

def BRgbAnsiTC(R: int, G: int, B: int) -> string:
    return (f"\x1b[48;2;{R};{G};{B}m")

def FRgbAnsi(R: int, G: int, B: int) -> string:
    r = round((R / 256) * 5)
    g = round((G / 256) * 5)
    b = round((B / 256) * 5)
    color_code = r * 36 + g * 6 + b + 16
    return (f"\x1b[38;5;{color_code}m")

def BRgbAnsi(R: int, G: int, B: int) -> string:
    r = round((R / 255) * 5)
    g = round((G / 255) * 5)
    b = round((B / 255) * 5)
    color_code = r * 36 + g * 6 + b + 16
    return (f"\x1b[48;5;{color_code}m")

def bold(text):
    return "\x1b[1m" + text + "\x1b[22m"


def italic(text):
    return "\x1b[3m" + text + "\x1b[23m"


def underline(text):
    return "\x1b[4m" + text + "\x1b[24m"


def underline(text):
    return "\x1b[4m" + text + "\x1b[24m"


def blinking(text):
    return "\x1b[5m" + text + "\x1b[25m"


CR = "\x1b[0m"


def go_up(n_lines: int) -> str:
    return write(f"\033[{n_lines}F")


def go_up_() -> str:
    return write(f"\033M")

# clear console


def clear() -> int:
    return os.system("cls")


# get terminal size
def get_size() -> os.terminal_size:
    return os.get_terminal_size()

# formatting

def center(text: str, max_len: int, fill: str = " "):
    text_len = len(remove_ansi(text))
    pl = (max_len - text_len)//2
    pr = max_len - pl - text_len
    return (fill * pl) + text + (fill * pr)


def rjust(text: str, max_len: int, fill: str = " "):
    text_len = len(remove_ansi(text))
    pl = max_len - text_len
    return (fill * pl) + text


def ljust(text: str, max_len: int, fill: str = " "):
    text_len = len(remove_ansi(text))
    pr = max_len - text_len
    return text + (fill * pr)
