"""ISO 3166-2 PL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PL-02": (Entity("Dolnośląskie", "PL-02", "VOIVODSHIP", "pl", ""),),
        "PL-04": (Entity("Kujawsko-Pomorskie", "PL-04", "VOIVODSHIP", "pl", ""),),
        "PL-06": (Entity("Lubelskie", "PL-06", "VOIVODSHIP", "pl", ""),),
        "PL-08": (Entity("Lubuskie", "PL-08", "VOIVODSHIP", "pl", ""),),
        "PL-10": (Entity("Łódzkie", "PL-10", "VOIVODSHIP", "pl", ""),),
        "PL-12": (Entity("Małopolskie", "PL-12", "VOIVODSHIP", "pl", ""),),
        "PL-14": (Entity("Mazowieckie", "PL-14", "VOIVODSHIP", "pl", ""),),
        "PL-16": (Entity("Opolskie", "PL-16", "VOIVODSHIP", "pl", ""),),
        "PL-18": (Entity("Podkarpackie", "PL-18", "VOIVODSHIP", "pl", ""),),
        "PL-20": (Entity("Podlaskie", "PL-20", "VOIVODSHIP", "pl", ""),),
        "PL-22": (Entity("Pomorskie", "PL-22", "VOIVODSHIP", "pl", ""),),
        "PL-24": (Entity("Śląskie", "PL-24", "VOIVODSHIP", "pl", ""),),
        "PL-26": (Entity("Świętokrzyskie", "PL-26", "VOIVODSHIP", "pl", ""),),
        "PL-28": (Entity("Warmińsko-Mazurskie", "PL-28", "VOIVODSHIP", "pl", ""),),
        "PL-30": (Entity("Wielkopolskie", "PL-30", "VOIVODSHIP", "pl", ""),),
        "PL-32": (Entity("Zachodniopomorskie", "PL-32", "VOIVODSHIP", "pl", ""),),
    }
