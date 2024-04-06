"""
Absfuyu: WGS
------------
Wolf's Gravestone

- This module is not affiliated with miHoYo/Hoyoverse.
- Genshin Impact, game content and materials are trademarks and copyrights of miHoYo/Hoyoverse.

Version: 1.0.3
Date updated: 24/11/2023 (dd/mm/yyyy)

Usage:
------
>>> test = WGS()
>>> print(test.pixel_art())
"""


# Module level
###########################################################################
__all__ = ["WGS"]


# Library
###########################################################################
import base64

from absfuyu.logger import logger
from absfuyu.tools.converter import Str2Pixel


# Class
###########################################################################
class WGS:
    """
    Wolf's Gravestone

    - This module is not affiliated with miHoYo/Hoyoverse.
    - Genshin Impact, game content and materials are trademarks and copyrights of miHoYo/Hoyoverse.
    """

    def __init__(self) -> None:
        self._text_art_big = "ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuLjo9KzoKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgID0qKioqKi4gCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuPSojKisrCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAtIyslKyA6LgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLSMjJSsuCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC4qIyUqLgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IyMlPQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA9IyMjOgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICArIyUrICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAtIyMjLQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA9KyAgICA9JSMjLiAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDojIyUrLi4tLT0tIDojIyo9KiMlJT0gICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICMlJSUlIyUjIyUlJSUlJSMjIyUlOgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgOj0lJUAlIyMjIyUjJSUlJSUlPS0tOiAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuJSo6JSUjJSUlIyMlJSUlJSUqPSAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IyM9KysjJSMjKyolJSMlJSo6ICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDo9KiojIyMjJSMlIyUlJSUlJSUjKyAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC49KyoqIyUlJSMjIyUjIyUlJSUlJSsgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAqJSMjIyUjIyMjQCMlIys9LSNAJSUjKz0tICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgOisqIyVAJSUjIyUlJSMlIyUjKiouOislJSMjLiAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAtKiMjJSVAJSUlJSUlIyUtLis9ICAgICA6Ky0tLiAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC0qIyMlQEAlIyVAQCUjJUArIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC4tIyUlJUAlJUBAIyUlIyouICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuPSMjJSUlJSUlJSUjJSU9LiAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuLSojJSUlJSUlQCUlJSMqLSAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuOiolJSUlJSUlJSUlIyorLgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgOiojJSUlJSUlJSUlIz06ICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC4gLSMjIyMjIyUlJSUlIy0gCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA9IyMjIyUjIyUlIz0qLiAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgOisjIyMjIyMlJSUqLS0uIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuLSojIyMjJSMlJSUqLTouIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA9KysqKioqIyMqKj0tLiAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuLSsqKiorKiojIyMqPTogCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLSsrKysqIyMrKiMqPS4gIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgLjorKiojIyMjIyUjKj0tICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgIC4gOisqIyMjIyMjIyMqPTogIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgLiA9KyojKisjIyMjIystIAogICAgICAgICAgICAgICAgICAgICAgICAuIC49KiojKi0qIyMjKj0tICAKICAgICAgICAgICAgICAgICAgICAgICAgOisqKiMrPSojIyMqPToKICAgICAgICAgICAgICAgICAgICAgICAgLSsqKiotPSoqKyorPS4KICAgICAgICAgICAgICAgICAgICAgICAgLj0rKiorLSojKioqKy0uICAKICAgICAgICAgICAgICAgICAgICAuOi09KyoqLT0jIyoqKz06IAogICAgICAgICAgICAgICAgICAgIDotPSsrKiotKyMqKiorLSAKICAgICAgICAgICAgICAgICAgICA6PSsrKyAgOioqKis9OiAgICAKICAgICAgICAgICAgICAgIDo9KyoqLS09KioqKz06IAogICAgICAgICAgICAgICAgLT0rKiotKysrKz06LiAgCiAgICAgICAgICAgICAgICA6PT0rKis6PT06LiAgCiAgICAgICAgICAgIDo9KysqLQogICAgICAgICAgICAuLT0rKy0uIAogICAgICAgIC46PS06LiAgICAKICAgICAgICAuOjouICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAK"
        self._text_art_small = "CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgOjoKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAuKiorCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgLiojLi4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDojKwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPSM6CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIC4uICAqKgogICAgICAgICAgICAgICAgICAgICAgICAgICAgPSUrPSsrIyMqIyoKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICArKiUjJSMlJSM9CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKyoqIyMjJSUlPQogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICsjIyUjIyMqKiUjOgogICAgICAgICAgICAgICAgICAgICAgICAgICAgLisjJSUlJSUrKjogLSotCiAgICAgICAgICAgICAgICAgICAgICAgICAgICA9IyUlJSUlKy4KICAgICAgICAgICAgICAgICAgICAgICAgICAgIC49IyUlJSUjPQogICAgICAgICAgICAgICAgICAgICAgICAuKiUlJSUlKy4KICAgICAgICAgICAgICAgICAgICAgICAgLiojJSUlIy0KICAgICAgICAgICAgICAgICAgICAgICAgLSMjIyUjPS4KICAgICAgICAgICAgICAgICAgICAuPSoqKiMqOgogICAgICAgICAgICAgICAgICAgIDorKiMjKisuCiAgICAgICAgICAgICAgICAgICAgLSoqIyMjLQogICAgICAgICAgICAgICAgLj0qKyojKjoKICAgICAgICAgICAgICAgIDorKisqKj0uCiAgICAgICAgICAgICAgICAuLSsrKyoqLQogICAgICAgICAgICAuPSotLSorOgogICAgICAgICAgICAuPSs9PS0uCiAgICAgICAgICAgIDorPQogICAgICAgIC46Lgo="
        self._pixel_art_wgs = [
            # Art Credit: https://www.reddit.com/r/PixelArt/comments/n6xyrb/wolfs_gravestone_genshin_impact/
            "51w",
            "46w3b1w",
            "43w2b1w1b1R1b1w",
            "43w1b1R1b1R2b1w",
            "43w2b1r1b3w",
            "41w3b1r1b1r1b2w",
            "28w3b10w1b1g5b2w",
            "28w1b1r1b9w1b3g1b5w",
            "28w2b1R1b1w2b4w1b3g2b5w",
            "30w1b1m1b1g1b1w1b1w1b3g1b7w",
            "30w3b2g3b3g1b8w",
            "29w1b2g1b5g1b1g1b9w",
            "29w1b1g2b1g4b1g1b10w",
            "29w1b3g2b1R2b1g2b9w",
            "27w7b3r1b1g1b10w",
            "27w1b5g1b1r1w2b2g2b8w",
            "26w2b3g6b4g1b8w",
            "26w1b2g2b2R1b1g1b1g4b9w",
            "25w1b2g1b2R2r1b1g1b1g1b1g1b1m1b8w",
            "24w1b1w1m1g1b3r1b2g1b3g2b1R2b6w",
            "21w3b2w1m1b3r1w1b2g4b2w1b1r1b6w",
            "21w1b2w3m1b1r1w2b3g1b5w3b6w",
            "21w1b1w3m1b1r2b3g3b14w",
            "20w1b1w2R1m1b1r1b3m1g2b16w",
            "19w1b1w3R1b1r1b2m2w1b18w",
            "18w1b1w3R1b1r1b3m1w1b19w",
            "17w1b1r3R1b1w1b2R1m1w1b20w",
            "16w1b1w1R1r1R1b1r1b3R2w1b20w",
            "15w1b1w1r1R1y1R2b3R1w3b20w",
            "14w1b3r1y1R2r4y1b23w",
            "13w1b1w3r4y2R1w1b24w",
            "12w1b1w2r2R3r1R2y1b25w",
            "10w2b1w2r1R2b1R3r1w1b26w",
            "9w1b2w2r1R1b1w1b1R2r1w1b27w",
            "9w1b1w2r1R1b1w1b1R2r1y1b28w",
            "8w1b1w1r2R1b1w1b2r1y1w1b29w",
            "7w1b1w1r1R2b1w1b4y1b30w",
            "6w1b1w1r1R1b2w1b1R2r1w1b31w",
            "5w1b1w2r1R1b2w1b1R1r2w1b31w",
            "4w1b1w2r1R1b1w2b2r1w2b32w",
            "3w1b1w1r1y1R1b1w1b3y1w1b34w",
            "2w1b1w1r2y1b1w6b35w",
            "1w6b43w",
            "50w",
        ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def _base64_decode(base64_text: str) -> str:
        return base64.b64decode(base64_text).decode()

    def text_art(self, option: int = 1) -> str:
        """
        Text art

        :param option: ``1`` | ``2``
        :type option: int
        :rtype: str
        """
        if option == 1:
            return self._base64_decode(self._text_art_big)
        else:
            return self._base64_decode(self._text_art_small)

    def pixel_art(self) -> str:
        """
        Pixel art

        :rtype: str
        """
        # Make data
        out = "1N".join(self._pixel_art_wgs)
        out = out.replace("y", "r")  # Convert yellow into red
        out = out.replace("m", "R")  # Convert magenta into dark red
        return Str2Pixel(out).convert()


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
    test = WGS()
    print(test.pixel_art())
