"""ISO 3166-2 LS standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LS
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LS-A": (
            Entity("Maseru", "LS-A", "DISTRICT", "en", ""),
            Entity("Maseru", "LS-A", "DISTRICT", "st", ""),
        ),
        "LS-B": (
            Entity("Botha-Bothe", "LS-B", "DISTRICT", "en", ""),
            Entity("Botha-Bothe", "LS-B", "DISTRICT", "st", ""),
        ),
        "LS-C": (
            Entity("Leribe", "LS-C", "DISTRICT", "en", ""),
            Entity("Leribe", "LS-C", "DISTRICT", "st", ""),
        ),
        "LS-D": (
            Entity("Berea", "LS-D", "DISTRICT", "en", ""),
            Entity("Berea", "LS-D", "DISTRICT", "st", ""),
        ),
        "LS-E": (
            Entity("Mafeteng", "LS-E", "DISTRICT", "en", ""),
            Entity("Mafeteng", "LS-E", "DISTRICT", "st", ""),
        ),
        "LS-F": (
            Entity("Mohale's Hoek", "LS-F", "DISTRICT", "en", ""),
            Entity("Mohale's Hoek", "LS-F", "DISTRICT", "st", ""),
        ),
        "LS-G": (
            Entity("Quthing", "LS-G", "DISTRICT", "en", ""),
            Entity("Quthing", "LS-G", "DISTRICT", "st", ""),
        ),
        "LS-H": (
            Entity("Qacha's Nek", "LS-H", "DISTRICT", "en", ""),
            Entity("Qacha's Nek", "LS-H", "DISTRICT", "st", ""),
        ),
        "LS-J": (
            Entity("Mokhotlong", "LS-J", "DISTRICT", "en", ""),
            Entity("Mokhotlong", "LS-J", "DISTRICT", "st", ""),
        ),
        "LS-K": (
            Entity("Thaba-Tseka", "LS-K", "DISTRICT", "en", ""),
            Entity("Thaba-Tseka", "LS-K", "DISTRICT", "st", ""),
        ),
    }
