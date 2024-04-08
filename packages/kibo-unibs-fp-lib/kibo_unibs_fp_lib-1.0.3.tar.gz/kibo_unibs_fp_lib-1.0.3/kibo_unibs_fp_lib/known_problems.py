"""Module for the KnownProblems class"""


class KnownProblems:
    """
    This class has the implementation of some of the usual problems that you always forget and need
    to go watch the solution on StackOverflow even though you know you've already solved them.
    """

    def __init__(self) -> None:
        """Prevents instantiation of this class

        Raises:
            NotImplementedError
        """

        raise NotImplementedError()

    @staticmethod
    def mcd(a: int, b: int) -> int:
        """Finds the MCD (Maximum Common Divider) between two integers.

        Params:
            a -> The first number to calculate the MCD.

            b -> The second number to calculate the MCD.

        Returns:
            An integer representing the MCD.
        """

        while a != 0 and b != 0:
            if a > b:
                a %= b
            else:
                b %= a

        return b if a == 0 else a

    @staticmethod
    def mcd_array(values: list[int]) -> int:
        """Finds the MCD (Maximum Common Divider) between a list of integers.

        Params:
            values -> The values used to find the MCD.

        Returns:
            An integer representing the MCD between all the values. If values is None or an empty
            array, -1 will be returned.
        """

        if not values:
            return -1

        mcd = values[0]

        for value in values[1:]:
            mcd = KnownProblems.mcd(mcd, value)

        return mcd

    @staticmethod
    def mcm(a: int, b: int) -> int:
        """Finds the MCM (Minimum Common Multiplier) between two numbers.

        Params:
            a -> The first number to calculate the MCM.

            b -> The second number to calculate the MCM.

        Returns:
            An integer representing the MCM.
        """

        mcd = KnownProblems.mcd(a, b)

        return (a * b) // mcd

    @staticmethod
    def mcm_array(values: list[int]) -> int:
        """Finds the MCM (Minimum Common Multiplier) between a list of integers.

        Params:
            values -> The values used to find the MCM.

        Returns:
            An integer representing the MCM between all the values. If values is None or an empty
            array, -1 will be returned.
        """

        if not values:
            return -1

        mcm = values[0]

        for value in values[1:]:
            mcm = KnownProblems.mcm(mcm, value)

        return mcm

    @staticmethod
    def count_integer_digits(n: int) -> int:
        """Counts the number of digits of an integer.

        Params:
            n -> The number to calculate the digits.

        Returns:
            An integer representing the number of digits of n.
        """

        return len(str(abs(n)))

    @staticmethod
    def count_decimal_digits(n: float) -> int:
        """
        Counts the number of decimal digits in a float.

        Params:
            n -> The number to calculate the decimal digits.

        Returns:
            An integer representing the number of decimal digits of n.
        """

        decimal_str = str(abs(n)).split(".")[1]

        return len(decimal_str) if decimal_str else 0
