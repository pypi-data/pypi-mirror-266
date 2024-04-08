"""Module for the Menu class"""

# Standard Libraries
import os
import time

# Internal Libraries
from kibo_unibs_fp_lib.ansi_colors import ansi_colors
from kibo_unibs_fp_lib.input_data import InputData
from kibo_unibs_fp_lib.known_problems import KnownProblems
from kibo_unibs_fp_lib.pretty_strings import PrettyStrings


class Menu:
    """
    This class creates a menu with multiple entries, assuming that zero is always the exit option.
    The class also contains some methods that may be useful for visualizing the menu.
    """

    _NEW_LINE = "\n"
    _EXIT_ENTRY = "0. Exit"
    _INSERT_REQUEST = "> "
    _NEGATIVE_MILLIS_ERROR = (
        f"{ansi_colors["red"]}Attention!{ansi_colors["reset"]}\nYou can't have negative time."
    )

    def __init__(
        self,
        title: str,
        entries: list[str],
        use_exit_entry: bool,
        centred_title: bool,
    ) -> None:
        """Constructor that creates a Menu object specifying a title, the entries of the menu, if 
        you want the exit entry or not, if you want the title centred, and the vertical frame will 
        be off by default. It will also automatically calculate the frame length.

        Params:
            title -> Represents the title of the menu.

            entries -> Represents the entries of the menu.

            use_exit_entry -> If you want the exit entry or not.

            centred_title -> If you want the title to be centred or not.

            use_vertical_frame -> If you want to use the vertical frame or not.
        """

        self._title = title
        self._entries = entries
        self._use_exit_entry = use_exit_entry
        self._frame_length = Menu._calculate_frame_length(title, entries)
        self._centred_title = centred_title
        self._use_vertical_frame = False

    @property
    def use_vertical_frame(self) -> bool:
        """Getter of attribute use_vertical_frame.
        
        Returns:
            A bool representing the current value of use_vertical_frame.
        """

        return self._use_vertical_frame

    @use_vertical_frame.setter
    def use_vertical_frame(self, value: bool) -> None:
        """Setter of attribute use_vertical_frame.
        
        Params:
            value -> The new value of use_vertical_frame.
        """

        self._use_vertical_frame = value

    @staticmethod
    def _calculate_frame_length(title: str, entries: list[str]) -> int:
        """Calculates the frame length by measuring the length of the title and of all the entries
        of the menu, accounting for their number and the ". " string before the actual entry.

        Params:
            title -> The title of the menu.

            entries -> The entries of the menu.

        Returns:
            An integer representing the length of the frame.
        """

        frame_length = len(title)

        for i, entry in enumerate(entries):
            frame_length = max(
                frame_length, len(entry) + KnownProblems.count_integer_digits(i + 1) + 2
            )

        return frame_length + 10  # Adding a bit of extra space

    def _print_menu(self) -> None:
        """
        Prints the menu: first the framed title and then all the entries.
        """

        menu = []

        menu.append(
            PrettyStrings.frame(
                self._title,
                self._frame_length,
                self._centred_title,
                self._use_vertical_frame,
            )
        )

        for i, entry in enumerate(self._entries):
            to_append = f"{i+1}. {entry}{self._NEW_LINE}"

            menu.append(to_append)

        if self._use_exit_entry:
            menu.append(PrettyStrings.isolated_line(self._EXIT_ENTRY))

        print("".join(menu))

    def choose(self) -> int:
        """Prints the menu and lets the user choose an option from it.

        Returns:
            An integer representing the choice of the user.
        """

        self._print_menu()

        if self._use_exit_entry:
            min_value = 0
        else:
            min_value = 1

        return InputData.read_integer_between(
            self._INSERT_REQUEST, min_value, len(self._entries)
        )

    @staticmethod
    def clear_console() -> None:
        """
        Clear the console screen.
        """

        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def wait(milliseconds: int) -> None:
        """Stops the program for a certain amount of milliseconds.

        Params:
            milliseconds -> The number of milliseconds to stop the program.
        """

        if milliseconds < 0:
            print(Menu._NEGATIVE_MILLIS_ERROR)
            return

        time.sleep(milliseconds / 1000)

    @staticmethod
    def loading_message(message: str) -> None:
        """Prints a certain message simulating a loading by adding dots slowly.

        Params:
            message -> The message to print.
        """

        print(message, end="", flush=True)
        for _ in range(3):
            Menu.wait(1000)
            print(".", end="", flush=True)

        Menu.clear_console()
