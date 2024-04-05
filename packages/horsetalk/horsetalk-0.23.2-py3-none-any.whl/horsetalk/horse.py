import re

import pendulum

from .breed import Breed
from .horse_age import HorseAge


class Horse:
    """A class used to represent a Horse.

    Attributes:
        name (str): The name of the horse.
        breed (Breed): The breed of the horse.
        country (str): The country where the horse was bred.
        age (HorseAge): The age of the horse.

    Args:
        name (str): The name of the horse.
        country (str, optional): The country where the horse was bred. Defaults to None.
        age_or_yob (int, optional): The age or year of birth of the horse. Defaults to None.
        context_date (datetime, optional): The context date used to calculate the age of the horse. Defaults to current date.
    """

    REGEX = re.compile(
        r"""
        (?P<name>[A-Za-z]{1}[A-Za-z ']{1,19}[A-Za-z]{1})            # Horse's name
        \s*                                                         # Optional whitespace
        (?:\((?P<country>\w+)\))?                                   # Country of origin
        \s*                                                         # Optional whitespace
        (?P<age_or_yob>\d{1,4})?                                    # Age or year of birth
    """,
        re.VERBOSE,
    )

    def __init__(self, name, country=None, age_or_yob=None, *, context_date=None):
        """Initializes the Horse object with name, country, age_or_yob, and context_date.

        Args:
            name (str): The name of the horse.
            country (str, optional): The country where the horse was bred. Defaults to None.
            age_or_yob (int, optional): The age or year of birth of the horse. Defaults to None.
            context_date (datetime, optional): The context date used to calculate the age of the horse. Defaults to current date.
        """
        match = re.match(Horse.REGEX, name)

        if not context_date:
            context_date = pendulum.now()

        self.name = match.group("name")
        self.breed = None if len(self.name) <= 18 else Breed.AQPS
        self.country = match.group("country") or country

        if country and country != self.country:
            raise ValueError(
                f"Conflicting countries in name and country arguments: {country}"
            )

        if (
            age_or_yob
            and match.group("age_or_yob")
            and int(match.group("age_or_yob")) != age_or_yob
        ):
            raise ValueError(
                f"Conflicting age_or_yob in name and age_or_yob arguments: {age_or_yob}"
            )

        age_or_yob = int(match.group("age_or_yob") or age_or_yob or -1)

        if age_or_yob > 999:
            self.age = HorseAge(birth_year=age_or_yob, context_date=context_date)
        elif age_or_yob > 0:
            self.age = HorseAge(age_or_yob, context_date=context_date)
        else:
            self.age = None
