"""ISO 3166-2 BA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BA-BIH": (
            Entity("Federacija Bosne i Hercegovine", "BA-BIH", "ENTITY", "bs", ""),
            Entity("Federacija Bosne i Hercegovine", "BA-BIH", "ENTITY", "hr", ""),
            Entity("Federacija Bosne i Hercegovine", "BA-BIH", "ENTITY", "sr", ""),
        ),
        "BA-BRC": (
            Entity("Brčko distrikt", "BA-BRC", "DISTRICT WITH SPECIAL STATUS", "bs", ""),
            Entity("Brčko distrikt", "BA-BRC", "DISTRICT WITH SPECIAL STATUS", "hr", ""),
            Entity("Brčko distrikt", "BA-BRC", "DISTRICT WITH SPECIAL STATUS", "sr", ""),
        ),
        "BA-SRP": (
            Entity("Republika Srpska", "BA-SRP", "ENTITY", "bs", ""),
            Entity("Republika Srpska", "BA-SRP", "ENTITY", "hr", ""),
            Entity("Republika Srpska", "BA-SRP", "ENTITY", "sr", ""),
        ),
    }
