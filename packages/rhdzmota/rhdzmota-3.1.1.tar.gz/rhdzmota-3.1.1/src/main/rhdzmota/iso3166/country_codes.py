import os
import enum
import json
from typing import Dict
from dataclasses import dataclass


from rhdzmota.settings import logger_manager


logger = logger_manager.get_logger(name=__name__)


@dataclass
class CountryInfo:
    num: int
    name: str
    alpha_code_2: str
    alpha_code_3: str


def get_country_metadata() -> Dict[str, CountryInfo]:
    filepath = os.path.join(os.path.dirname(__file__), "datafiles", "countries.json")
    with open(filepath, "r") as file:
        payload = json.loads(file.read())
    return {
        alpha_code_2: CountryInfo(
            alpha_code_2=alpha_code_2,
            **info
        )
        for alpha_code_2, info in payload.items()
    }


class _CountryEnumBase(enum.Enum):

    @property
    def subdivisions_data_filepath(self) -> str:
        filename = f"{self.name}.json".lower()
        filepath = os.path.join(os.path.dirname(__file__), "datafiles", filename)
        if os.path.exists(filepath):
            return filepath
        logger.error("Missing datafile for %s (%s)", self.name, filepath)
        return os.path.join(os.path.dirname(filepath), "default.json")

    @property
    def subdivisions(self) -> enum.Enum:
        data_filepath = self.subdivisions_data_filepath
        with open(data_filepath, "r") as file:
            payload = json.loads(file.read())
        return enum.Enum(self.name, payload)


Country = _CountryEnumBase("Country", get_country_metadata())  # type: ignore
