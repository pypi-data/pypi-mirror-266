"""ISO 3166-2 JO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:JO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "JO-AJ": (Entity("‘Ajlūn", "JO-AJ", "GOVERNORATE", "ar", ""),),
        "JO-AM": (Entity("Al ‘A̅şimah", "JO-AM", "GOVERNORATE", "ar", ""),),
        "JO-AQ": (Entity("Al ‘Aqabah", "JO-AQ", "GOVERNORATE", "ar", ""),),
        "JO-AT": (Entity("Aţ Ţafīlah", "JO-AT", "GOVERNORATE", "ar", ""),),
        "JO-AZ": (Entity("Az Zarqā’", "JO-AZ", "GOVERNORATE", "ar", ""),),
        "JO-BA": (Entity("Al Balqā’", "JO-BA", "GOVERNORATE", "ar", ""),),
        "JO-IR": (Entity("Irbid", "JO-IR", "GOVERNORATE", "ar", ""),),
        "JO-JA": (Entity("Jarash", "JO-JA", "GOVERNORATE", "ar", ""),),
        "JO-KA": (Entity("Al Karak", "JO-KA", "GOVERNORATE", "ar", ""),),
        "JO-MA": (Entity("Al Mafraq", "JO-MA", "GOVERNORATE", "ar", ""),),
        "JO-MD": (Entity("Mādabā", "JO-MD", "GOVERNORATE", "ar", ""),),
        "JO-MN": (Entity("Ma‘ān", "JO-MN", "GOVERNORATE", "ar", ""),),
    }
