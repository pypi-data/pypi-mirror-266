import pybud
import pybud.ansi as ansi
from pybud.ansi import ColorType
from pybud.drawer import ColoredString as CStr
from pybud.gui.gui import AutoDialouge
from pybud.gui.utils import Point, Size
from pybud.gui.widgets import WidgetInput, WidgetLabel, WidgetOptions


def input_dialouge(WIDTH=76):
    """ the main dialouge """

    title = CStr("[") + CStr(" " + "PyBUD: GUI Beauty" +
                             " ", forecolor=(255, 0, 0)) + CStr("]")
    caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialouges, Widgets, Drawables, color optimization, and more!"
    mydialouge = AutoDialouge(width=WIDTH, ctype=ColorType.LEGACY)

    mydialouge.add_widget(WidgetLabel(
        title,
        size=Size(WIDTH),  # height will be owerwritten in WidgetLabel
        pos=Point(0, 1),
    ))

    mydialouge.add_widget(WidgetLabel(
        caption,
        centered=True,
        size=Size(WIDTH),  # height will be owerwritten in WidgetLabel
        pos=Point(0, 2),
    ))

    mydialouge.add_widget(WidgetInput(
        "text input: ",
        size=Size(WIDTH//2 - 4),  # height will be owerwritten in WidgetLabel
        pos=Point(2, 6),
    ))
    mydialouge.add_widget(WidgetInput(
        "another text input: ",
        size=Size(WIDTH//2 - 4),  # height will be owerwritten in WidgetLabel
        pos=Point(WIDTH//2 + 2, 6),
    ))

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

    def awesome_option(self):
        ansi.write("Awesome!          \r")
        ansi.flush()
        return "Awesome!"
    # the text and callback function for each option
    options = [
        ("Nice!", nice_option),
        ("Very Cool!", verycool_option),
        ("Awesome!", awesome_option),
        ("Briliant!", briliant_option),
    ]
    mydialouge.add_widget(WidgetOptions(
        options,
        size=Size(WIDTH-4),  # height will be owerwritten in WidgetOptions
        pos=Point(2, 8),
    ))
    mydialouge.add_widget(WidgetLabel(
        CStr("Tip: ", forecolor=(220, 220, 0)) +
        CStr("you can use TAB or arrow keys to switch between selectable Widgets! and use ") + CStr("Ctrl + C", forecolor=(220, 220, 0)) +
        CStr(" or press enter on (InputWidget)s to exit!"),
        centered=True,
        size=Size(WIDTH - 24),  # height will be owerwritten in WidgetLabel
        pos=Point(22, 9),
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

    mydialouge = input_dialouge()

    # mydialouge.show()
    text = mydialouge.show()

    print(f"result (last callback return): \"{text}\"")

    print(f"individual outputs:")
    for i, w in enumerate(mydialouge.widgets):
        if isinstance(w, WidgetInput):
            print(f"text written in textbox ({w.text}): ", w.input)
        if isinstance(w, WidgetOptions):
            print("selected option id:", w.selected, "selected option text:", w.options[w.selected])



