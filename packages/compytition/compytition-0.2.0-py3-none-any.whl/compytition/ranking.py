from typing import Any

from .rank import Rank
from .rank_list import RankList


class Ranking(dict):
    """
    A class used to represent a Ranking.

    This class is a dictionary subclass that maps any key to a rank, which can be an integer, a string, or a Rank object.
    The ranks must be consecutive and account for ties.

    Attributes
    ----------
    ranking : dict[Any, int | str | Rank]
        A dictionary mapping keys to ranks.

    Methods
    -------
    __init__(self, ranking: dict[Any, int | str | Rank])
        Initializes the Ranking with a dictionary of ranks.
    """

    def __init__(self, ranking: dict[Any, int | str | Rank]) -> None:
        """
        Initializes the Ranking with a dictionary of ranks.

        The ranks are converted to Rank objects, and then checked to ensure they are consecutive and account for ties.
        If the ranks are not consecutive or do not account for ties, a ValueError is raised.

        Parameters
        ----------
        ranking : dict[Any, int | str | Rank]
            A dictionary mapping keys to ranks.

        Raises
        ------
        ValueError
            If the ranks are not consecutive or do not account for ties.
        """
        ranking = {k: Rank(v) for k, v in ranking.items()}
        RankList(ranking.values())
        
        super().__init__(ranking)