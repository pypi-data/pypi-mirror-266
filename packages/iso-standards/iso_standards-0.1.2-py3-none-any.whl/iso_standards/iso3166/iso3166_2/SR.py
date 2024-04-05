"""ISO 3166-2 SR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SR-BR": (Entity("Brokopondo", "SR-BR", "DISTRICT", "nl", ""),),
        "SR-CM": (Entity("Commewijne", "SR-CM", "DISTRICT", "nl", ""),),
        "SR-CR": (Entity("Coronie", "SR-CR", "DISTRICT", "nl", ""),),
        "SR-MA": (Entity("Marowijne", "SR-MA", "DISTRICT", "nl", ""),),
        "SR-NI": (Entity("Nickerie", "SR-NI", "DISTRICT", "nl", ""),),
        "SR-PM": (Entity("Paramaribo", "SR-PM", "DISTRICT", "nl", ""),),
        "SR-PR": (Entity("Para", "SR-PR", "DISTRICT", "nl", ""),),
        "SR-SA": (Entity("Saramacca", "SR-SA", "DISTRICT", "nl", ""),),
        "SR-SI": (Entity("Sipaliwini", "SR-SI", "DISTRICT", "nl", ""),),
        "SR-WA": (Entity("Wanica", "SR-WA", "DISTRICT", "nl", ""),),
    }
