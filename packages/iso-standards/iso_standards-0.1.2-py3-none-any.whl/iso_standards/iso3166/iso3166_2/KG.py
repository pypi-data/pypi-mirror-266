"""ISO 3166-2 KG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KG-B": (
            Entity("Batken", "KG-B", "REGION", "ky", ""),
            Entity("Batkenskaja oblast'", "KG-B", "REGION", "ru", ""),
            Entity("Batkenskaya oblast'", "KG-B", "REGION", "ru", ""),
        ),
        "KG-C": (
            Entity("Chuyskaya oblast'", "KG-C", "REGION", "ru", ""),
            Entity("Chüy", "KG-C", "REGION", "ky", ""),
            Entity("Čujskaja oblast'", "KG-C", "REGION", "ru", ""),
        ),
        "KG-GB": (
            Entity("Bishkek Shaary", "KG-GB", "CITY", "ky", ""),
            Entity("Gorod Bishkek", "KG-GB", "CITY", "ru", ""),
            Entity("Gorod Biškek", "KG-GB", "CITY", "ru", ""),
        ),
        "KG-GO": (
            Entity("Gorod Osh", "KG-GO", "CITY", "ru", ""),
            Entity("Gorod Oš", "KG-GO", "CITY", "ru", ""),
            Entity("Osh Shaary", "KG-GO", "CITY", "ky", ""),
        ),
        "KG-J": (
            Entity("Dzhalal-Abadskaya oblast'", "KG-J", "REGION", "ru", ""),
            Entity("Džalal-Abadskaja oblast'", "KG-J", "REGION", "ru", ""),
            Entity("Jalal-Abad", "KG-J", "REGION", "ky", ""),
        ),
        "KG-N": (
            Entity("Naryn", "KG-N", "REGION", "ky", ""),
            Entity("Narynskaja oblast'", "KG-N", "REGION", "ru", ""),
            Entity("Narynskaya oblast'", "KG-N", "REGION", "ru", ""),
        ),
        "KG-O": (
            Entity("Osh", "KG-O", "REGION", "ky", ""),
            Entity("Oshskaya oblast'", "KG-O", "REGION", "ru", ""),
            Entity("Ošskaja oblast'", "KG-O", "REGION", "ru", ""),
        ),
        "KG-T": (
            Entity("Talas", "KG-T", "REGION", "ky", ""),
            Entity("Talasskaja oblast'", "KG-T", "REGION", "ru", ""),
            Entity("Talasskaya oblast'", "KG-T", "REGION", "ru", ""),
        ),
        "KG-Y": (
            Entity("Issyk-Kul'skaja oblast'", "KG-Y", "REGION", "ru", ""),
            Entity("Issyk-Kul'skaya oblast'", "KG-Y", "REGION", "ru", ""),
            Entity("Ysyk-Köl", "KG-Y", "REGION", "ky", ""),
        ),
    }
