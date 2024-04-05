"""ISO 3166-2 SE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SE-AB": (Entity("Stockholms län", "SE-AB", "COUNTY", "sv", ""),),
        "SE-AC": (Entity("Västerbottens län", "SE-AC", "COUNTY", "sv", ""),),
        "SE-BD": (Entity("Norrbottens län", "SE-BD", "COUNTY", "sv", ""),),
        "SE-C": (Entity("Uppsala län", "SE-C", "COUNTY", "sv", ""),),
        "SE-D": (Entity("Södermanlands län", "SE-D", "COUNTY", "sv", ""),),
        "SE-E": (Entity("Östergötlands län", "SE-E", "COUNTY", "sv", ""),),
        "SE-F": (Entity("Jönköpings län", "SE-F", "COUNTY", "sv", ""),),
        "SE-G": (Entity("Kronobergs län", "SE-G", "COUNTY", "sv", ""),),
        "SE-H": (Entity("Kalmar län", "SE-H", "COUNTY", "sv", ""),),
        "SE-I": (Entity("Gotlands län", "SE-I", "COUNTY", "sv", ""),),
        "SE-K": (Entity("Blekinge län", "SE-K", "COUNTY", "sv", ""),),
        "SE-M": (Entity("Skåne län", "SE-M", "COUNTY", "sv", ""),),
        "SE-N": (Entity("Hallands län", "SE-N", "COUNTY", "sv", ""),),
        "SE-O": (Entity("Västra Götalands län", "SE-O", "COUNTY", "sv", ""),),
        "SE-S": (Entity("Värmlands län", "SE-S", "COUNTY", "sv", ""),),
        "SE-T": (Entity("Örebro län", "SE-T", "COUNTY", "sv", ""),),
        "SE-U": (Entity("Västmanlands län", "SE-U", "COUNTY", "sv", ""),),
        "SE-W": (Entity("Dalarnas län", "SE-W", "COUNTY", "sv", ""),),
        "SE-X": (Entity("Gävleborgs län", "SE-X", "COUNTY", "sv", ""),),
        "SE-Y": (Entity("Västernorrlands län", "SE-Y", "COUNTY", "sv", ""),),
        "SE-Z": (Entity("Jämtlands län", "SE-Z", "COUNTY", "sv", ""),),
    }
