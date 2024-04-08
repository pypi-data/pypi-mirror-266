from typing import Any, Self

from peak_utility.number import Ordinal  # type: ignore


class Rank(Ordinal):
    """
    A class used to represent a Rank.

    Attributes
    ----------
    tied : bool
        a flag indicating whether the rank is tied with another

    Methods
    -------
    __new__(cls, value, **kwargs)
        Creates a new instance of the Rank class.
    __repr__()
        Returns a string representation of the Rank object.
    __str__()
        Returns a string of the Rank object.
    """

    def __new__(cls, value: int | str, **kwargs: Any) -> Self:
        """
        Creates a new instance of the Rank class.

        Parameters
        ----------
        cls : Any
            The class that is being instantiated.
        value : Any
            The value of the rank.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        Any
            A new instance of the Rank class.
        """
        instance = super().__new__(cls, str(value).replace("=", ""))    
        instance.tied = kwargs.get('tied', "=" in str(value))
        return instance

    def __repr__(self) -> str:
        """
        Returns a representation of the Rank object.

        Returns
        -------
        str
            A representation of the Rank object.
        """
        return f"{super().__repr__()}{'=' if self.tied else ''}"

    def __str__(self) -> str:
        """
        Returns a string of the Rank object.

        Returns
        -------
        str
            A string of the Rank object.
        """
        return f"{int(self)}{'=' if self.tied else ''}"