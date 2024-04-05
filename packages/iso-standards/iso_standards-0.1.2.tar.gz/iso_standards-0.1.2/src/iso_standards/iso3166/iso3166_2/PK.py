"""ISO 3166-2 PK standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PK
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PK-BA": (
            Entity("Balochistan", "PK-BA", "PROVINCE", "en", ""),
            Entity("Balōchistān", "PK-BA", "PROVINCE", "ur", ""),
        ),
        "PK-GB": (
            Entity("Gilgit-Baltistan", "PK-GB", "PAKISTAN ADMINISTERED AREA", "en", ""),
            Entity("Gilgit-Baltistān", "PK-GB", "PAKISTAN ADMINISTERED AREA", "ur", ""),
        ),
        "PK-IS": (
            Entity("Islamabad", "PK-IS", "FEDERAL CAPITAL TERRITORY", "en", ""),
            Entity("Islāmābād", "PK-IS", "FEDERAL CAPITAL TERRITORY", "ur", ""),
        ),
        "PK-JK": (
            Entity("Azad Jammu and Kashmir", "PK-JK", "PAKISTAN ADMINISTERED AREA", "en", ""),
            Entity("Āzād Jammūñ o Kashmīr", "PK-JK", "PAKISTAN ADMINISTERED AREA", "ur", ""),
        ),
        "PK-KP": (
            Entity("Khaībar Pakhtūnkhwā", "PK-KP", "PROVINCE", "ur", ""),
            Entity("Khyber Pakhtunkhwa", "PK-KP", "PROVINCE", "en", ""),
        ),
        "PK-PB": (
            Entity("Panjāb", "PK-PB", "PROVINCE", "ur", ""),
            Entity("Punjab", "PK-PB", "PROVINCE", "en", ""),
        ),
        "PK-SD": (
            Entity("Sindh", "PK-SD", "PROVINCE", "en", ""),
            Entity("Sindh", "PK-SD", "PROVINCE", "ur", ""),
        ),
    }
