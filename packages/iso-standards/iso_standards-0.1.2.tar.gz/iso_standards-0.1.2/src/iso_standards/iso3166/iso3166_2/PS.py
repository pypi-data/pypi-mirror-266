"""ISO 3166-2 PS standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PS
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PS-BTH": (
            Entity("Bayt Laḩm", "PS-BTH", "GOVERNORATE", "ar", ""),
            Entity("Bethlehem", "PS-BTH", "GOVERNORATE", "en", ""),
        ),
        "PS-DEB": (
            Entity("Dayr al Balaḩ", "PS-DEB", "GOVERNORATE", "ar", ""),
            Entity("Deir El Balah", "PS-DEB", "GOVERNORATE", "en", ""),
        ),
        "PS-GZA": (
            Entity("Gaza", "PS-GZA", "GOVERNORATE", "en", ""),
            Entity("Ghazzah", "PS-GZA", "GOVERNORATE", "ar", ""),
        ),
        "PS-HBN": (
            Entity("Al Khalīl", "PS-HBN", "GOVERNORATE", "ar", ""),
            Entity("Hebron", "PS-HBN", "GOVERNORATE", "en", ""),
        ),
        "PS-JEM": (
            Entity("Al Quds", "PS-JEM", "GOVERNORATE", "ar", ""),
            Entity("Jerusalem", "PS-JEM", "GOVERNORATE", "en", ""),
        ),
        "PS-JEN": (
            Entity("Janīn", "PS-JEN", "GOVERNORATE", "ar", ""),
            Entity("Jenin", "PS-JEN", "GOVERNORATE", "en", ""),
        ),
        "PS-JRH": (
            Entity("Arīḩā wal Aghwār", "PS-JRH", "GOVERNORATE", "ar", ""),
            Entity("Jericho and Al Aghwar", "PS-JRH", "GOVERNORATE", "en", ""),
        ),
        "PS-KYS": (
            Entity("Khan Yunis", "PS-KYS", "GOVERNORATE", "en", ""),
            Entity("Khān Yūnis", "PS-KYS", "GOVERNORATE", "ar", ""),
        ),
        "PS-NBS": (
            Entity("Nablus", "PS-NBS", "GOVERNORATE", "en", ""),
            Entity("Nāblus", "PS-NBS", "GOVERNORATE", "ar", ""),
        ),
        "PS-NGZ": (
            Entity("North Gaza", "PS-NGZ", "GOVERNORATE", "en", ""),
            Entity("Shamāl Ghazzah", "PS-NGZ", "GOVERNORATE", "ar", ""),
        ),
        "PS-QQA": (
            Entity("Qalqilya", "PS-QQA", "GOVERNORATE", "en", ""),
            Entity("Qalqīlyah", "PS-QQA", "GOVERNORATE", "ar", ""),
        ),
        "PS-RBH": (
            Entity("Ramallah", "PS-RBH", "GOVERNORATE", "en", ""),
            Entity("Rām Allāh wal Bīrah", "PS-RBH", "GOVERNORATE", "ar", ""),
        ),
        "PS-RFH": (
            Entity("Rafah", "PS-RFH", "GOVERNORATE", "en", ""),
            Entity("Rafaḩ", "PS-RFH", "GOVERNORATE", "ar", ""),
        ),
        "PS-SLT": (
            Entity("Salfit", "PS-SLT", "GOVERNORATE", "en", ""),
            Entity("Salfīt", "PS-SLT", "GOVERNORATE", "ar", ""),
        ),
        "PS-TBS": (
            Entity("Tubas", "PS-TBS", "GOVERNORATE", "en", ""),
            Entity("Ţūbās", "PS-TBS", "GOVERNORATE", "ar", ""),
        ),
        "PS-TKM": (
            Entity("Tulkarm", "PS-TKM", "GOVERNORATE", "en", ""),
            Entity("Ţūlkarm", "PS-TKM", "GOVERNORATE", "ar", ""),
        ),
    }
