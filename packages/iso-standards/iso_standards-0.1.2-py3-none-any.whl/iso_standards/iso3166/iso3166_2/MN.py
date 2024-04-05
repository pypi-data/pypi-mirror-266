"""ISO 3166-2 MN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MN-035": (Entity("Orhon", "MN-035", "PROVINCE", "mn", ""),),
        "MN-037": (Entity("Darhan uul", "MN-037", "PROVINCE", "mn", ""),),
        "MN-039": (Entity("Hentiy", "MN-039", "PROVINCE", "mn", ""),),
        "MN-041": (Entity("Hövsgöl", "MN-041", "PROVINCE", "mn", ""),),
        "MN-043": (Entity("Hovd", "MN-043", "PROVINCE", "mn", ""),),
        "MN-046": (Entity("Uvs", "MN-046", "PROVINCE", "mn", ""),),
        "MN-047": (Entity("Töv", "MN-047", "PROVINCE", "mn", ""),),
        "MN-049": (Entity("Selenge", "MN-049", "PROVINCE", "mn", ""),),
        "MN-051": (Entity("Sühbaatar", "MN-051", "PROVINCE", "mn", ""),),
        "MN-053": (Entity("Ömnögovĭ", "MN-053", "PROVINCE", "mn", ""),),
        "MN-055": (Entity("Övörhangay", "MN-055", "PROVINCE", "mn", ""),),
        "MN-057": (Entity("Dzavhan", "MN-057", "PROVINCE", "mn", ""),),
        "MN-059": (Entity("Dundgovĭ", "MN-059", "PROVINCE", "mn", ""),),
        "MN-061": (Entity("Dornod", "MN-061", "PROVINCE", "mn", ""),),
        "MN-063": (Entity("Dornogovĭ", "MN-063", "PROVINCE", "mn", ""),),
        "MN-064": (Entity("Govĭ-Sümber", "MN-064", "PROVINCE", "mn", ""),),
        "MN-065": (Entity("Govĭ-Altay", "MN-065", "PROVINCE", "mn", ""),),
        "MN-067": (Entity("Bulgan", "MN-067", "PROVINCE", "mn", ""),),
        "MN-069": (Entity("Bayanhongor", "MN-069", "PROVINCE", "mn", ""),),
        "MN-071": (Entity("Bayan-Ölgiy", "MN-071", "PROVINCE", "mn", ""),),
        "MN-073": (Entity("Arhangay", "MN-073", "PROVINCE", "mn", ""),),
        "MN-1": (Entity("Ulaanbaatar", "MN-1", "CAPITAL CITY", "mn", ""),),
    }
