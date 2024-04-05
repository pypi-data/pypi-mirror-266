"""ISO 3166-2 IN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:IN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "IN-AN": (Entity("Andaman and Nicobar Islands", "IN-AN", "UNION TERRITORY", "en", ""),),
        "IN-AP": (Entity("Andhra Pradesh", "IN-AP", "STATE", "en", ""),),
        "IN-AR": (Entity("Arunāchal Pradesh", "IN-AR", "STATE", "en", ""),),
        "IN-AS": (Entity("Assam", "IN-AS", "STATE", "en", ""),),
        "IN-BR": (Entity("Bihār", "IN-BR", "STATE", "en", ""),),
        "IN-CG": (Entity("Chhattīsgarh", "IN-CG", "STATE", "en", ""),),
        "IN-CH": (Entity("Chandīgarh", "IN-CH", "UNION TERRITORY", "en", ""),),
        "IN-DH": (
            Entity(
                "Dādra and Nagar Haveli and Damān and Diu", "IN-DH", "UNION TERRITORY", "en", ""
            ),
        ),
        "IN-DL": (Entity("Delhi", "IN-DL", "UNION TERRITORY", "en", ""),),
        "IN-GA": (Entity("Goa", "IN-GA", "STATE", "en", ""),),
        "IN-GJ": (Entity("Gujarāt", "IN-GJ", "STATE", "en", ""),),
        "IN-HP": (Entity("Himāchal Pradesh", "IN-HP", "STATE", "en", ""),),
        "IN-HR": (Entity("Haryāna", "IN-HR", "STATE", "en", ""),),
        "IN-JH": (Entity("Jhārkhand", "IN-JH", "STATE", "en", ""),),
        "IN-JK": (Entity("Jammu and Kashmīr", "IN-JK", "UNION TERRITORY", "en", ""),),
        "IN-KA": (Entity("Karnātaka", "IN-KA", "STATE", "en", ""),),
        "IN-KL": (Entity("Kerala", "IN-KL", "STATE", "en", ""),),
        "IN-LA": (Entity("Ladākh", "IN-LA", "UNION TERRITORY", "en", ""),),
        "IN-LD": (Entity("Lakshadweep", "IN-LD", "UNION TERRITORY", "en", ""),),
        "IN-MH": (Entity("Mahārāshtra", "IN-MH", "STATE", "en", ""),),
        "IN-ML": (Entity("Meghālaya", "IN-ML", "STATE", "en", ""),),
        "IN-MN": (Entity("Manipur", "IN-MN", "STATE", "en", ""),),
        "IN-MP": (Entity("Madhya Pradesh", "IN-MP", "STATE", "en", ""),),
        "IN-MZ": (Entity("Mizoram", "IN-MZ", "STATE", "en", ""),),
        "IN-NL": (Entity("Nāgāland", "IN-NL", "STATE", "en", ""),),
        "IN-OD": (Entity("Odisha", "IN-OD", "STATE", "en", ""),),
        "IN-PB": (Entity("Punjab", "IN-PB", "STATE", "en", ""),),
        "IN-PY": (Entity("Puducherry", "IN-PY", "UNION TERRITORY", "en", ""),),
        "IN-RJ": (Entity("Rājasthān", "IN-RJ", "STATE", "en", ""),),
        "IN-SK": (Entity("Sikkim", "IN-SK", "STATE", "en", ""),),
        "IN-TN": (Entity("Tamil Nādu", "IN-TN", "STATE", "en", ""),),
        "IN-TR": (Entity("Tripura", "IN-TR", "STATE", "en", ""),),
        "IN-TS": (Entity("Telangāna", "IN-TS", "STATE", "en", ""),),
        "IN-UK": (Entity("Uttarākhand", "IN-UK", "STATE", "en", ""),),
        "IN-UP": (Entity("Uttar Pradesh", "IN-UP", "STATE", "en", ""),),
        "IN-WB": (Entity("West Bengal", "IN-WB", "STATE", "en", ""),),
    }
