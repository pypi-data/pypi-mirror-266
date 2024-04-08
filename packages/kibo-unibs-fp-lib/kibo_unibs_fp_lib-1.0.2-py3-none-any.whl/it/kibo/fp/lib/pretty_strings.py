"""Module for the PrettyStrings class"""


class PrettyStrings:
    """
    This class contains various methods to better print strings to the terminal.
    """

    _SPACE = " "
    _HORIZONTAL_FRAME = "-"
    _VERTICAL_FRAME = "|"
    _NEW_LINE = "\n"

    def __init__(self) -> None:
        """Prevents instantiation of this class

        Raises:
            NotImplementedError
        """

        raise NotImplementedError()

    @staticmethod
    def frame(
        to_frame: str, frame_length: int, centered: bool, vertical_frame: bool
    ) -> str:
        """Puts the given string in the center or in the beginning of the line surrounded by the
        horizontal frame above and below and, if needed, also the vertical frame before and after.
        It's required to specify a frame length for the horizontal frame.

        Params:
            to_frame -> The string to put in the frame

            frame_length -> The length of the horizontal frame.

            centered -> If the string needs to be centered or not.

            vertical_frame -> If the vertical frame is needed or not.

        Returns:
            A string containing the framed original string.
        """

        framed = []

        framed.append(
            PrettyStrings.repeat_char(PrettyStrings._HORIZONTAL_FRAME, frame_length)
            + PrettyStrings._NEW_LINE
        )

        if vertical_frame:
            framed.append(PrettyStrings._VERTICAL_FRAME)

        if centered:
            framed.append(
                PrettyStrings.center(to_frame, frame_length - 2)
                if vertical_frame
                else PrettyStrings.center(to_frame, frame_length)
                + PrettyStrings._NEW_LINE
            )
        else:
            framed.append(
                PrettyStrings.column(to_frame, frame_length - 2)
                if vertical_frame
                else PrettyStrings.column(to_frame, frame_length)
                + PrettyStrings._NEW_LINE
            )

        if vertical_frame:
            framed.append(PrettyStrings._VERTICAL_FRAME + PrettyStrings._NEW_LINE)

        framed.append(
            PrettyStrings.repeat_char(PrettyStrings._HORIZONTAL_FRAME, frame_length)
            + PrettyStrings._NEW_LINE
        )

        return "".join(framed)

    @staticmethod
    def column(to_columnize: str, width: int) -> str:
        """Puts teh given string at the beginning of the line and adds _SPACEs until the end of the
        line. If the string is too long for the width of the line, it will be cut off.

        Params:
            to_columnize -> The string to put in column.

            width -> The length of the line.

        Returns:
            A string containing the columned string.
        """

        to_columnize_length = len(to_columnize)
        char_to_print = min(width, to_columnize_length)
        columned = to_columnize[:char_to_print]
        columned += PrettyStrings.repeat_char(
            PrettyStrings._SPACE, max(0, width - to_columnize_length)
        )

        return columned

    @staticmethod
    def center(to_center: str, width: int) -> str:
        """Puts the given string in the center of the line of the given length. If the string is
        too long it will be cut off.

        Params:
            to_center -> The string to center.

            width -> The length of the line where to center the string.
        """

        to_center_length = len(to_center)
        if width < to_center_length:
            centred = to_center[:width]
        elif width == to_center_length:
            centred = to_center
        else:
            white_spaces = width - to_center_length
            spaces_before = white_spaces // 2
            spaces_after = white_spaces - spaces_before

            centred = PrettyStrings.repeat_char(PrettyStrings._SPACE, spaces_before)
            centred += to_center
            centred += PrettyStrings.repeat_char(PrettyStrings._SPACE, spaces_after)

        return centred

    @staticmethod
    def repeat_char(char: str, times: int) -> str:
        """Repeats a given character a given number of times.

        Params:
            char -> The character to repeat.

            times -> The number of times to repeat the character.

        Returns:
            A string containing the character repeated.
        """

        return char * max(0, times)

    @staticmethod
    def isolated_line(to_isolate: str) -> str:
        """Isolated a given string by adding an empty line before and after it.

        Params:
            to_isolate -> The string to isolate.

        Returns:
            A string containing the isolated string.
        """

        return PrettyStrings._NEW_LINE + to_isolate + PrettyStrings._NEW_LINE
