"""ISO 3166-2 KM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KM-A": (
            Entity("Andjouân", "KM-A", "ISLAND", "ar", ""),
            Entity("Anjouan", "KM-A", "ISLAND", "fr", ""),
            Entity("Anjwān", "KM-A", "ISLAND", "ar", ""),
            Entity("Ndzuwani", "KM-A", "ISLAND", "", ""),
        ),
        "KM-G": (
            Entity("Andjazîdja", "KM-G", "ISLAND", "ar", ""),
            Entity("Anjazījah", "KM-G", "ISLAND", "ar", ""),
            Entity("Grande Comore", "KM-G", "ISLAND", "fr", ""),
            Entity("Ngazidja", "KM-G", "ISLAND", "", ""),
        ),
        "KM-M": (
            Entity("Mohéli", "KM-M", "ISLAND", "fr", ""),
            Entity("Moûhîlî", "KM-M", "ISLAND", "ar", ""),
            Entity("Mwali", "KM-M", "ISLAND", "", ""),
            Entity("Mūhīlī", "KM-M", "ISLAND", "ar", ""),
        ),
    }
