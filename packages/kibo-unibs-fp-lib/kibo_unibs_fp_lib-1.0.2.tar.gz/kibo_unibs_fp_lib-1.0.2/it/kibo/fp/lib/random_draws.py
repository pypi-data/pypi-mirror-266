"""Module for the RandomDraws class"""

# Standard Libraries
import random


class RandomDraws:
    """
    This class provides methods for drawing a specific data type in a pseudo-random way.
    """

    _RAND = random.Random()

    def __init__(self) -> None:
        """Prevents instantiation of this class

        Raises:
            NotImplementedError
        """

        raise NotImplementedError()

    @staticmethod
    def draw_integer(minimum: int, maximum: int) -> int:
        """Draws a random integer between given minimum and maximum values.

        Params:
            minimum -> The minimum value to draw.
            maximum -> The maximum value to draw

        Returns:
            An integer representing the drawn number.
        """

        return RandomDraws._RAND.randint(minimum, maximum)

    @staticmethod
    def draw_float(minimum: float, maximum: float) -> float:
        """Draws a random float between given minimum and maximum values.

        Params:
            minimum -> The minimum value to draw.
            maximum -> The maximum value to draw

        Returns:
            An float representing the drawn number.
        """

        return RandomDraws._RAND.uniform(minimum, maximum)

    @staticmethod
    def draw_integer_with_distribution(
        minimum: int, maximum: int, exponent: float
    ) -> int:
        """Draws a random integer between given minimum and maximum values, with a certain
        distribution. In order to distribute the values you use the exponent:
        • exponent &#8804; 0: Completely random values will be given, almost always not between the
        given minimum and maximum values. This usage is not encouraged.

        • 0 < exponent < 1: The values near the maximum have a greater probability of being drawn,
        closer the exponent is to 0.

        • exponent = 1: All the values have the same probability of being drawn.

        • exponent &#8805; 1: The values near the minimum have a greater probability of being
        drawn, greater exponents will increase this probability.

        Params:
            minimum -> The minimum value to draw.

            maximum -> The maximum value to draw.

            exponent -> The exponent of the distribution.

        Returns:
            An integer representing the drawn number.
        """

        drawing_range = maximum + 1 - minimum
        random_float = RandomDraws._RAND.random() ** exponent

        return minimum + int(drawing_range * random_float)

    @staticmethod
    def draw_bool() -> bool:
        """Draws a random bool.

        Returns:
            The drawn boolean.
        """

        return RandomDraws._RAND.choice([True, False])
