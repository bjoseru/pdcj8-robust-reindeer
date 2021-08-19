from pathlib import Path
from typing import Callable

from asciimatics.exceptions import StopApplication
from asciimatics.scene import Scene
from asciimatics.widgets import Button, Divider, Frame, Layout, TextBox
from asciimatics.screen import Screen

from .data_structures import HelpEntry

HELP = [
    HelpEntry(name, Path(path).read_text())
    for name, path in (
        ("Overview", "docs/overview.md"),
        ("Mouse Movements", "docs/mouse_movements.md"),
        ("Keyboard Commands", "docs/keyboard_commands.md"),
        ("More Info", "docs/more_info.md"),
    )
]

BRIEF_HELP_TEXT = """
 Rotate Front: f/F;
 Rotate Middle: m/M;
 Rotate Back: b/B;
 Rotate Top: t/T;
 Rotate Bottom: d/D;
 Rotate Left: l/L;
 Rotate Right: r/R;
 Reset View: z;
 Show HELP: h;
 Quit: q/Q;
 Mouse Click: Enable/disable free rotation of the cube;
 Mouse Drag: Rotate the cube;
"""


class HelpMenu(Frame):
    """The HelpMenu class to render and display a dynamic help menu."""

    def __init__(self, screen: Screen):
        super().__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            can_scroll=False,
            title="Robust Reindeers - Rubik's Cube Help"
        )
        self.palette["layout"] = (0, 0, 0)

        self._long_help_box = TextBox(
            screen.height * 2 // 3 - 10,
            as_string=True,
            line_wrap=True,
            readonly=True,
        )
        self._long_help_box.custom_colour = "title"
        self._long_help_box.value = HELP[0].description

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Divider())

        for index, entry in enumerate(HELP):
            button = Button(entry.name, self._button_wrapper(index))
            layout.add_widget(button)

        layout.add_widget(Divider())
        layout.add_widget(self._long_help_box)

        layout.add_widget(Divider())
        layout.add_widget(Button("Return to Game", self._quit))

        self.should_quit = False
        self.fix()

    def _button_wrapper(self, index: int) -> Callable[..., None]:
        """Return a wrapper that will update the extended help menu when a button of this index is pressed."""
        def wrapper() -> None:
            help = HELP[index]
            self._long_help_box.value = f"{help.name}::\n{help.description}"

        return wrapper

    def _quit(self) -> None:
        """Quit the help session."""
        raise StopApplication("user quit")


def show_help(screen: Screen, log) -> None:
    """Show the help session, respond to user input and return to the cube once the user clicks the Quit button."""
    screen.clear_buffer(0, 0, 0)
    screen.refresh()

    screen.play([Scene([HelpMenu(screen)], -1, name="Help Menu")])

    log.info("got to the end")
    screen.clear_buffer(0, 0, 0)
    screen.refresh()
