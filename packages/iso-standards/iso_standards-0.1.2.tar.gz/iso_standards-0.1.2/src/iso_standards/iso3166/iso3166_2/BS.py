"""ISO 3166-2 BS standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BS
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BS-AK": (Entity("Acklins", "BS-AK", "DISTRICT", "en", ""),),
        "BS-BI": (Entity("Bimini", "BS-BI", "DISTRICT", "en", ""),),
        "BS-BP": (Entity("Black Point", "BS-BP", "DISTRICT", "en", ""),),
        "BS-BY": (Entity("Berry Islands", "BS-BY", "DISTRICT", "en", ""),),
        "BS-CE": (Entity("Central Eleuthera", "BS-CE", "DISTRICT", "en", ""),),
        "BS-CI": (Entity("Cat Island", "BS-CI", "DISTRICT", "en", ""),),
        "BS-CK": (Entity("Crooked Island and Long Cay", "BS-CK", "DISTRICT", "en", ""),),
        "BS-CO": (Entity("Central Abaco", "BS-CO", "DISTRICT", "en", ""),),
        "BS-CS": (Entity("Central Andros", "BS-CS", "DISTRICT", "en", ""),),
        "BS-EG": (Entity("East Grand Bahama", "BS-EG", "DISTRICT", "en", ""),),
        "BS-EX": (Entity("Exuma", "BS-EX", "DISTRICT", "en", ""),),
        "BS-FP": (Entity("City of Freeport", "BS-FP", "DISTRICT", "en", ""),),
        "BS-GC": (Entity("Grand Cay", "BS-GC", "DISTRICT", "en", ""),),
        "BS-HI": (Entity("Harbour Island", "BS-HI", "DISTRICT", "en", ""),),
        "BS-HT": (Entity("Hope Town", "BS-HT", "DISTRICT", "en", ""),),
        "BS-IN": (Entity("Inagua", "BS-IN", "DISTRICT", "en", ""),),
        "BS-LI": (Entity("Long Island", "BS-LI", "DISTRICT", "en", ""),),
        "BS-MC": (Entity("Mangrove Cay", "BS-MC", "DISTRICT", "en", ""),),
        "BS-MG": (Entity("Mayaguana", "BS-MG", "DISTRICT", "en", ""),),
        "BS-MI": (Entity("Moore's Island", "BS-MI", "DISTRICT", "en", ""),),
        "BS-NE": (Entity("North Eleuthera", "BS-NE", "DISTRICT", "en", ""),),
        "BS-NO": (Entity("North Abaco", "BS-NO", "DISTRICT", "en", ""),),
        "BS-NP": (Entity("New Providence", "BS-NP", "ISLAND", "en", ""),),
        "BS-NS": (Entity("North Andros", "BS-NS", "DISTRICT", "en", ""),),
        "BS-RC": (Entity("Rum Cay", "BS-RC", "DISTRICT", "en", ""),),
        "BS-RI": (Entity("Ragged Island", "BS-RI", "DISTRICT", "en", ""),),
        "BS-SA": (Entity("South Andros", "BS-SA", "DISTRICT", "en", ""),),
        "BS-SE": (Entity("South Eleuthera", "BS-SE", "DISTRICT", "en", ""),),
        "BS-SO": (Entity("South Abaco", "BS-SO", "DISTRICT", "en", ""),),
        "BS-SS": (Entity("San Salvador", "BS-SS", "DISTRICT", "en", ""),),
        "BS-SW": (Entity("Spanish Wells", "BS-SW", "DISTRICT", "en", ""),),
        "BS-WG": (Entity("West Grand Bahama", "BS-WG", "DISTRICT", "en", ""),),
    }
