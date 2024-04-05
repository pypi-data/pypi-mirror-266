"""ISO 3166-2 EG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:EG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "EG-ALX": (Entity("Al Iskandarīyah", "EG-ALX", "GOVERNORATE", "ar", ""),),
        "EG-ASN": (Entity("Aswān", "EG-ASN", "GOVERNORATE", "ar", ""),),
        "EG-AST": (Entity("Asyūţ", "EG-AST", "GOVERNORATE", "ar", ""),),
        "EG-BA": (Entity("Al Baḩr al Aḩmar", "EG-BA", "GOVERNORATE", "ar", ""),),
        "EG-BH": (Entity("Al Buḩayrah", "EG-BH", "GOVERNORATE", "ar", ""),),
        "EG-BNS": (Entity("Banī Suwayf", "EG-BNS", "GOVERNORATE", "ar", ""),),
        "EG-C": (Entity("Al Qāhirah", "EG-C", "GOVERNORATE", "ar", ""),),
        "EG-DK": (Entity("Ad Daqahlīyah", "EG-DK", "GOVERNORATE", "ar", ""),),
        "EG-DT": (Entity("Dumyāţ", "EG-DT", "GOVERNORATE", "ar", ""),),
        "EG-FYM": (Entity("Al Fayyūm", "EG-FYM", "GOVERNORATE", "ar", ""),),
        "EG-GH": (Entity("Al Gharbīyah", "EG-GH", "GOVERNORATE", "ar", ""),),
        "EG-GZ": (Entity("Al Jīzah", "EG-GZ", "GOVERNORATE", "ar", ""),),
        "EG-IS": (Entity("Al Ismā'īlīyah", "EG-IS", "GOVERNORATE", "ar", ""),),
        "EG-JS": (Entity("Janūb Sīnā'", "EG-JS", "GOVERNORATE", "ar", ""),),
        "EG-KB": (Entity("Al Qalyūbīyah", "EG-KB", "GOVERNORATE", "ar", ""),),
        "EG-KFS": (Entity("Kafr ash Shaykh", "EG-KFS", "GOVERNORATE", "ar", ""),),
        "EG-KN": (Entity("Qinā", "EG-KN", "GOVERNORATE", "ar", ""),),
        "EG-LX": (Entity("Al Uqşur", "EG-LX", "GOVERNORATE", "ar", ""),),
        "EG-MN": (Entity("Al Minyā", "EG-MN", "GOVERNORATE", "ar", ""),),
        "EG-MNF": (Entity("Al Minūfīyah", "EG-MNF", "GOVERNORATE", "ar", ""),),
        "EG-MT": (Entity("Maţrūḩ", "EG-MT", "GOVERNORATE", "ar", ""),),
        "EG-PTS": (Entity("Būr Sa‘īd", "EG-PTS", "GOVERNORATE", "ar", ""),),
        "EG-SHG": (Entity("Sūhāj", "EG-SHG", "GOVERNORATE", "ar", ""),),
        "EG-SHR": (Entity("Ash Sharqīyah", "EG-SHR", "GOVERNORATE", "ar", ""),),
        "EG-SIN": (Entity("Shamāl Sīnā'", "EG-SIN", "GOVERNORATE", "ar", ""),),
        "EG-SUZ": (Entity("As Suways", "EG-SUZ", "GOVERNORATE", "ar", ""),),
        "EG-WAD": (Entity("Al Wādī al Jadīd", "EG-WAD", "GOVERNORATE", "ar", ""),),
    }
