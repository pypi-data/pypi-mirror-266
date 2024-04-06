"""
Absfuyu: Tarot
--------------
Tarot stuff


Version: 1.0.3
Date updated: 01/01/2024 (dd/mm/yyyy)

Usage:
------
>>> tarot_deck = Tarot()
>>> print(tarot_deck.random_card())
"""

# Module level
###########################################################################
__all__ = ["Tarot", "TarotCard"]


# Library
###########################################################################
import random
from typing import Dict, List

from absfuyu.logger import logger
from absfuyu.pkg_data import DataList
from absfuyu.util.pkl import Pickler


# Class
###########################################################################
class TarotCard:
    """Tarot card"""

    def __init__(
        self,
        name: str,
        rank: int,
        suit: str,
        meanings: Dict[str, List[str]],
        keywords: List[str],
        fortune_telling: List[str],
    ) -> None:
        self.name = name.title()
        self.rank = rank
        self.suit = suit
        self.meanings = meanings
        self.keywords = keywords
        self.fortune_telling = fortune_telling

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return self.__str__()


class Tarot:
    """Tarot data"""

    def __init__(self) -> None:
        self.data_location = DataList.TAROT

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def tarot_deck(self) -> List[TarotCard]:
        """
        Load pickled tarot data

        :rtype: list[TarotCard]
        """
        tarot_data: list = Pickler.load(self.data_location)  # type: ignore
        logger.debug(f"{len(tarot_data)} tarot cards loaded")
        return [
            TarotCard(
                name=x["name"],
                rank=x["rank"],
                suit=x["suit"],
                meanings=x["meanings"],
                keywords=x["keywords"],
                fortune_telling=x["fortune_telling"],
            )
            for x in tarot_data
        ]

    def random_card(self) -> TarotCard:
        """
        Pick a random tarot card

        Returns
        -------
        TarotCard
            Random Tarot card
        """
        return random.choice(self.tarot_deck)


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
    pass
