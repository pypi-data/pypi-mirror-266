from collections import UserList
from typing import Sequence

from .rank import Rank


class RankList(UserList[Rank]):
    """
    Represents a list of ranks.
    
    Attributes
    ----------
    rank_list : List[Rank]
        A list of ranks.
    """

    def __init__(self, value: Sequence[Rank | int | str]) -> None:
        """
        Creates a new instance of the RankList class.

        Parameters
        ----------
        cls : Any
            The class that is being instantiated.
        value : Sequence[Rank | int | str]
            The value of the rank list.

        """
        previous_rank = 0
        tied = 0
        ranks = [Rank(x) for x in value]

        for rank in sorted(ranks, reverse=True):
            if rank == previous_rank:
                tied += 1
            elif int(previous_rank) + tied + 1 == int(rank): 
                tied = 0
            else:
                message = "Ranks must be consecutive" if tied == 0 else "Ranks must account for ties"
                raise ValueError(message)
    
            ranks.append(Rank(rank, tied=tied > 0))
            previous_rank = rank

        super().__init__(ranks)