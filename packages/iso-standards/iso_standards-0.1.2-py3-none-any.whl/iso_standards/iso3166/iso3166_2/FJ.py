"""ISO 3166-2 FJ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:FJ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "FJ-01": (Entity("Ba", "FJ-01", "PROVINCE", "en", "FJ-W"),),
        "FJ-02": (Entity("Bua", "FJ-02", "PROVINCE", "en", "FJ-N"),),
        "FJ-03": (Entity("Cakaudrove", "FJ-03", "PROVINCE", "en", "FJ-N"),),
        "FJ-04": (Entity("Kadavu", "FJ-04", "PROVINCE", "en", "FJ-E"),),
        "FJ-05": (Entity("Lau", "FJ-05", "PROVINCE", "en", "FJ-E"),),
        "FJ-06": (Entity("Lomaiviti", "FJ-06", "PROVINCE", "en", "FJ-E"),),
        "FJ-07": (Entity("Macuata", "FJ-07", "PROVINCE", "en", "FJ-N"),),
        "FJ-08": (Entity("Nadroga and Navosa", "FJ-08", "PROVINCE", "en", "FJ-W"),),
        "FJ-09": (Entity("Naitasiri", "FJ-09", "PROVINCE", "en", "FJ-C"),),
        "FJ-10": (Entity("Namosi", "FJ-10", "PROVINCE", "en", "FJ-C"),),
        "FJ-11": (Entity("Ra", "FJ-11", "PROVINCE", "en", "FJ-W"),),
        "FJ-12": (Entity("Rewa", "FJ-12", "PROVINCE", "en", "FJ-C"),),
        "FJ-13": (Entity("Serua", "FJ-13", "PROVINCE", "en", "FJ-C"),),
        "FJ-14": (Entity("Tailevu", "FJ-14", "PROVINCE", "en", "FJ-C"),),
        "FJ-C": (Entity("Central", "FJ-C", "DIVISION", "en", ""),),
        "FJ-E": (Entity("Eastern", "FJ-E", "DIVISION", "en", ""),),
        "FJ-N": (Entity("Northern", "FJ-N", "DIVISION", "en", ""),),
        "FJ-R": (Entity("Rotuma", "FJ-R", "DEPENDENCY", "en", ""),),
        "FJ-W": (Entity("Western", "FJ-W", "DIVISION", "en", ""),),
    }
