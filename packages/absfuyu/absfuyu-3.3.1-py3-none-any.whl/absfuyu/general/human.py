"""
Absfuyu: Human
--------------
Human related stuff

Version: 1.3.1
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Module level
###########################################################################
__all__ = ["Human", "Person"]


# Library
###########################################################################
from datetime import datetime, time
from typing import Optional, Union

from dateutil.relativedelta import relativedelta

from absfuyu.fun import zodiac_sign
from absfuyu.general.data_extension import IntNumber
from absfuyu.version import Version  # type: ignore


# Sub-Class
###########################################################################
class _FloatBase:
    """To show some unit"""

    def __init__(self, value: float) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value.__str__()

    def to_float(self) -> float:
        return float(self.value)


class _Height(_FloatBase):
    def __repr__(self) -> str:
        return f"{self.value:.2f} cm"


class _Weight(_FloatBase):
    def __repr__(self) -> str:
        return f"{self.value:.2f} kg"


# Class
###########################################################################
class BloodType:
    A_PLUS = "A+"
    A_MINUS = "A-"
    AB_PLUS = "AB+"
    AB_MINUS = "AB-"
    B_PLUS = "B+"
    B_MINUS = "B-"
    O_PLUS = "O+"
    O_MINUS = "O-"
    A = "A"
    AB = "AB"
    B = "B"
    O = "O"
    OTHER = None
    BLOOD_LIST = [A_MINUS, A_PLUS, B_MINUS, B_PLUS, AB_MINUS, AB_PLUS, O_MINUS, O_PLUS]


class Human:
    """
    Basic human data
    """

    __MEASUREMENT = "m|kg"  # Metric system
    __VERSION = Version(1, 1, 1)  # Internal version class check

    def __init__(
        self,
        first_name: str,
        last_name: Optional[str] = None,
        birthday: Union[str, datetime, None] = None,
        birth_time: Optional[str] = None,
        gender: Union[bool, None] = None,
    ) -> None:
        """
        :param first_name: First name
        :param last_name: Last name
        :param birthday: Birthday in format: ``yyyy/mm/dd``
        :param birth_time: Birth time in format: ``hh:mm``
        :param gender: ``True``: Male; ``False``: Female (biologicaly)
        """
        # Name
        self.first_name = first_name
        self.last_name = last_name
        self.name = (
            f"{self.last_name}, {self.first_name}"
            if self.last_name is not None
            else self.first_name
        )

        # Birthday
        now = datetime.now()
        if birthday is None:
            modified_birthday = now.date()
        elif isinstance(birthday, str):
            for x in ["/", "-"]:
                birthday = birthday.replace(x, "/")
            modified_birthday = datetime.strptime(birthday, "%Y/%m/%d")
        else:
            modified_birthday = birthday
            # birthday = list(map(int, birthday.split("/")))
            # modified_birthday = date(*birthday)
            # modified_birthday = date(birthday[0], birthday[1], birthday[2])

        if birth_time is None:
            modified_birthtime = now.time()
        else:
            birth_time = list(map(int, birth_time.split(":")))  # type: ignore
            modified_birthtime = time(*birth_time)
            # modified_birthtime = time(birth_time[0], birth_time[1])

        self.birthday = modified_birthday.date()  # type: ignore
        self.birth_time = modified_birthtime

        self.birth = datetime(
            modified_birthday.year,
            modified_birthday.month,
            modified_birthday.day,
            modified_birthtime.hour,
            modified_birthtime.minute,
        )

        # Others
        self.gender: bool = gender  # type: ignore # True: Male; False: Female
        self.height: float = None  # type: ignore # centimeter
        self.weight: float = None  # type: ignore # kilogram
        self.blood_type: Union[str, BloodType] = BloodType.OTHER  # type: ignore

    def __str__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({str(self.name)})"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        name = str(self.name)
        gender = "M" if self.is_male else "F"
        return f"{class_name}({name} ({self.age}|{gender}))"

    @classmethod
    def JohnDoe(cls):
        """
        Dummy Human for test

        Returns
        -------
        Human
            Dummy Human instance
        """
        temp = cls("John", "Doe", "1980/01/01", "00:00")
        temp.update({"gender": True, "height": 180, "weight": 80, "blood_type": "O+"})
        return temp

    @property
    def is_male(self) -> bool:
        """
        Check if male (biological)

        Returns
        -------
        bool
            | ``True``: Male
            | ``False``: Female
        """
        return self.gender

    @property
    def age(self):
        """
        Calculate age based on birthday

        Returns
        -------
        float
            Age

        None
            When unable to get ``self.birthday``
        """
        if self.birthday is not None:
            now = datetime.now()
            # age = now - self.birthday
            try:
                rdelta = relativedelta(now, self.birthday)
            except:
                date_str = self.birthday
                if date_str is None:
                    self.birthday = datetime.now().date()
                else:
                    for x in ["/", "-"]:
                        date_str = date_str.replace(x, "/")
                    date = datetime.strptime(date_str, "%Y/%m/%d")
                    self.birthday = date
                rdelta = relativedelta(now, self.birthday)
            return round(rdelta.years + rdelta.months / 12, 2)
        else:
            return None

    @property
    def is_adult(self):
        """
        Check if ``self.age`` >= ``18``

        :rtype: bool
        """
        return self.age >= 18

    @property
    def bmi(self):
        r"""
        Body Mass Index (kg/m^2)

        Formula: :math:`\frac{weight (kg)}{height (m)^2}`

        - BMI < 18.5: Skinny
        - 18.5 < BMI < 25: normal
        - BMI > 30: Obesse

        Returns
        -------
        float
            BMI value

        None
            When unable to get ``self.height`` and ``self.weight``
        """
        try:
            temp = self.height / 100
            bmi = self.weight / (temp * temp)
            return round(bmi, 2)
        except:
            return None

    # @property
    def dir_(self) -> list:
        """
        List property

        Returns
        -------
        list[str]
            List of available properties
        """
        return [x for x in self.__dir__() if not x.startswith("_")]

    def update(self, data: dict) -> None:
        """
        Update Human data

        Parameters
        ----------
        data : dict
            Data

        Returns
        -------
        None
        """
        self.__dict__.update(data)
        # return self


class Person(Human):
    """
    More detailed ``Human`` data
    """

    __VERSION = Version(1, 1, 1)  # Internal version class check

    def __init__(
        self,
        first_name: str,
        last_name: Optional[str] = None,
        birthday: Union[str, datetime, None] = None,
        birth_time: Optional[str] = None,
        gender: Union[bool, None] = None,
    ) -> None:
        super().__init__(first_name, last_name, birthday, birth_time, gender)
        self.address: str = None  # type: ignore
        self.hometown: str = None  # type: ignore
        self.email: str = None  # type: ignore
        self.phone_number: str = None  # type: ignore
        self.nationality = None  # type: ignore
        self.likes: list = None  # type: ignore
        self.hates: list = None  # type: ignore
        self.education = None  # type: ignore
        self.occupation: str = None  # type: ignore
        self.personality = None  # type: ignore
        self.note: str = None  # type: ignore

    @property
    def zodiac_sign(self):
        """
        Zodiac sign of ``Person``

        Returns
        -------
        str
            Zodiac sign

        None
            When unable to get ``self.birthday``
        """
        try:
            return zodiac_sign(self.birthday.day, self.birthday.month)
        except:
            return None

    @property
    def zodiac_sign_13(self):
        """
        Zodiac sign of ``Person`` (13 zodiac signs version)

        Returns
        -------
        str
            Zodiac sign

        None
            When unable to get ``self.birthday``
        """
        try:
            return zodiac_sign(self.birthday.day, self.birthday.month, zodiac13=True)
        except:
            return None

    @property
    def numerology(self) -> int:
        """
        Numerology number of ``Person``

        Returns
        -------
        int
            Numerology number
        """
        temp = f"{self.birthday.year}{self.birthday.month}{self.birthday.day}"
        return IntNumber(temp).add_to_one_digit(master_number=True)


# Run
###########################################################################
if __name__ == "__main__":
    print(Person.JohnDoe().__dict__)
