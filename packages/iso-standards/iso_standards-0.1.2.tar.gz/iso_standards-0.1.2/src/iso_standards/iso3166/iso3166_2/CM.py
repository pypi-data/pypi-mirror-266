"""ISO 3166-2 CM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CM-AD": (
            Entity("Adamaoua", "CM-AD", "REGION", "en", ""),
            Entity("Adamaoua", "CM-AD", "REGION", "fr", ""),
        ),
        "CM-CE": (
            Entity("Centre", "CM-CE", "REGION", "en", ""),
            Entity("Centre", "CM-CE", "REGION", "fr", ""),
        ),
        "CM-EN": (
            Entity("Extrême-Nord", "CM-EN", "REGION", "fr", ""),
            Entity("Far North", "CM-EN", "REGION", "en", ""),
        ),
        "CM-ES": (
            Entity("East", "CM-ES", "REGION", "en", ""),
            Entity("Est", "CM-ES", "REGION", "fr", ""),
        ),
        "CM-LT": (
            Entity("Littoral", "CM-LT", "REGION", "en", ""),
            Entity("Littoral", "CM-LT", "REGION", "fr", ""),
        ),
        "CM-NO": (
            Entity("Nord", "CM-NO", "REGION", "fr", ""),
            Entity("North", "CM-NO", "REGION", "en", ""),
        ),
        "CM-NW": (
            Entity("Nord-Ouest", "CM-NW", "REGION", "fr", ""),
            Entity("North-West", "CM-NW", "REGION", "en", ""),
        ),
        "CM-OU": (
            Entity("Ouest", "CM-OU", "REGION", "fr", ""),
            Entity("West", "CM-OU", "REGION", "en", ""),
        ),
        "CM-SU": (
            Entity("South", "CM-SU", "REGION", "en", ""),
            Entity("Sud", "CM-SU", "REGION", "fr", ""),
        ),
        "CM-SW": (
            Entity("South-West", "CM-SW", "REGION", "en", ""),
            Entity("Sud-Ouest", "CM-SW", "REGION", "fr", ""),
        ),
    }
