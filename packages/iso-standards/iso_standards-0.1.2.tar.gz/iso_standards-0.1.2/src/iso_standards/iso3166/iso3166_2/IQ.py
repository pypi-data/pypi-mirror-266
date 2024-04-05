"""ISO 3166-2 IQ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:IQ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "IQ-AN": (Entity("Al Anbār", "IQ-AN", "GOVERNORATE", "ar", ""),),
        "IQ-AR": (
            Entity("Arbīl", "IQ-AR", "GOVERNORATE", "ar", "IQ-KR"),
            Entity("Hewlêr", "IQ-AR", "GOVERNORATE", "ku", "IQ-KR"),
        ),
        "IQ-BA": (Entity("Al Başrah", "IQ-BA", "GOVERNORATE", "ar", ""),),
        "IQ-BB": (Entity("Bābil", "IQ-BB", "GOVERNORATE", "ar", ""),),
        "IQ-BG": (Entity("Baghdād", "IQ-BG", "GOVERNORATE", "ar", ""),),
        "IQ-DA": (
            Entity("Dahūk", "IQ-DA", "GOVERNORATE", "ar", "IQ-KR"),
            Entity("Dihok", "IQ-DA", "GOVERNORATE", "ku", "IQ-KR"),
        ),
        "IQ-DI": (Entity("Diyālá", "IQ-DI", "GOVERNORATE", "ar", ""),),
        "IQ-DQ": (Entity("Dhī Qār", "IQ-DQ", "GOVERNORATE", "ar", ""),),
        "IQ-KA": (Entity("Karbalā’", "IQ-KA", "GOVERNORATE", "ar", ""),),
        "IQ-KI": (Entity("Kirkūk", "IQ-KI", "GOVERNORATE", "ar", ""),),
        "IQ-KR": (
            Entity("Herêm-î Kurdistan", "IQ-KR", "REGION", "ku", ""),
            Entity("Iqlīm Kūrdistān", "IQ-KR", "REGION", "ar", ""),
        ),
        "IQ-MA": (Entity("Maysān", "IQ-MA", "GOVERNORATE", "ar", ""),),
        "IQ-MU": (Entity("Al Muthanná", "IQ-MU", "GOVERNORATE", "ar", ""),),
        "IQ-NA": (Entity("An Najaf", "IQ-NA", "GOVERNORATE", "ar", ""),),
        "IQ-NI": (Entity("Nīnawá", "IQ-NI", "GOVERNORATE", "ar", ""),),
        "IQ-QA": (Entity("Al Qādisīyah", "IQ-QA", "GOVERNORATE", "ar", ""),),
        "IQ-SD": (Entity("Şalāḩ ad Dīn", "IQ-SD", "GOVERNORATE", "ar", ""),),
        "IQ-SU": (
            Entity("As Sulaymānīyah", "IQ-SU", "GOVERNORATE", "ar", "IQ-KR"),
            Entity("Slêmanî", "IQ-SU", "GOVERNORATE", "ku", "IQ-KR"),
        ),
        "IQ-WA": (Entity("Wāsiţ", "IQ-WA", "GOVERNORATE", "ar", ""),),
    }
