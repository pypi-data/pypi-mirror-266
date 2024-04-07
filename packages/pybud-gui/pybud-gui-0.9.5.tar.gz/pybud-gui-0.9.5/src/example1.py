import pybud
import pybud.ansi as ansi
from pybud.drawer import ColoredString as CStr
from pybud.ansi import ColorType
from pybud.gui.gui import AutoDialouge
from pybud.gui.utils import Size, Point
from pybud.gui.widgets import WidgetInput, WidgetLabel, WidgetOptions


def main_dialouge(WIDTH = 70):
    """ the main dialouge """

    def briliant_option(self):
        ansi.write("Briliant!        \r")
        ansi.flush()
        return "Briliant!"

    def verycool_option(self):
        ansi.write("Very Cool!        \r")
        ansi.flush()
        return "Very Cool!"

    def nice_option(self):
        ansi.write("Nice!             \r")
        ansi.flush()
        return "Nice!"

    title = CStr("[") + CStr(" " + "PyBUD: GUI Beauty" +
                             " ", forecolor=(255, 0, 0)) + CStr("]")
    caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialouges, Widgets, Drawables, optimized colored strings, and more!"
    options = [
        ("Nice!", nice_option),
        ("Very Cool!", verycool_option),
        ("Briliant!", briliant_option),
    ]
    default = 2
    mydialouge = AutoDialouge(width=WIDTH, ctype=ColorType.LEGACY)
    mydialouge.add_widget(WidgetLabel(
        title,
        size=Size(WIDTH, 0),  # height will be owerwritten in WidgetLabel
        pos=Point(0, 1),
    ))
    mydialouge.add_widget(WidgetLabel(
        text = caption,
        centered=False,
        size=Size(WIDTH, 0),  # height will be owerwritten in WidgetLabel
        pos=Point(4, 2),
    ))

    mydialouge.add_widget(WidgetOptions(
        options,
        default_option=default,
        size=Size(WIDTH-4, 0),  # height will be owerwritten in WidgetOptions
        pos=Point(2, 6),
    ))

    return mydialouge

if __name__ == "__main__":
    ansi.InitAnsi()

    DEBUG = False

    if DEBUG:
        f = open("output.ansi", "w", encoding="utf-8")
        ansi.write = lambda x: f.write(x)
        ansi.writeln = lambda x: f.write(x + "\n")
        ansi.flush = lambda: f.flush()

    mydialouge = main_dialouge()
    try:
        # mydialouge.show()
        text = mydialouge.show()

        print(f"result: \"{text}\"")
        
    except KeyboardInterrupt:
        mydialouge.close()
