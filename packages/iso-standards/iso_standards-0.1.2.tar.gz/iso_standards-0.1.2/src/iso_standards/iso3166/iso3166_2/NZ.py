"""ISO 3166-2 NZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NZ-AUK": (
            Entity("Auckland", "NZ-AUK", "REGION", "en", ""),
            Entity("Tāmaki-Makaurau", "NZ-AUK", "REGION", "mi", ""),
        ),
        "NZ-BOP": (
            Entity("Bay of Plenty", "NZ-BOP", "REGION", "en", ""),
            Entity("Toi Moana", "NZ-BOP", "REGION", "mi", ""),
        ),
        "NZ-CAN": (
            Entity("Canterbury", "NZ-CAN", "REGION", "en", ""),
            Entity("Waitaha", "NZ-CAN", "REGION", "mi", ""),
        ),
        "NZ-CIT": (
            Entity("Chatham Islands Territory", "NZ-CIT", "SPECIAL ISLAND AUTHORITY", "en", ""),
            Entity("Wharekauri", "NZ-CIT", "SPECIAL ISLAND AUTHORITY", "mi", ""),
        ),
        "NZ-GIS": (
            Entity("Gisborne", "NZ-GIS", "REGION", "en", ""),
            Entity("Te Tairāwhiti", "NZ-GIS", "REGION", "mi", ""),
        ),
        "NZ-HKB": (
            Entity("Hawke's Bay", "NZ-HKB", "REGION", "en", ""),
            Entity("Te Matau-a-Māui", "NZ-HKB", "REGION", "mi", ""),
        ),
        "NZ-MBH": (Entity("Marlborough", "NZ-MBH", "REGION", "en", ""),),
        "NZ-MWT": (
            Entity("Manawatū Whanganui", "NZ-MWT", "REGION", "mi", ""),
            Entity("Manawatū-Whanganui", "NZ-MWT", "REGION", "en", ""),
        ),
        "NZ-NSN": (
            Entity("Nelson", "NZ-NSN", "REGION", "en", ""),
            Entity("Whakatū", "NZ-NSN", "REGION", "mi", ""),
        ),
        "NZ-NTL": (
            Entity("Northland", "NZ-NTL", "REGION", "en", ""),
            Entity("Te Taitokerau", "NZ-NTL", "REGION", "mi", ""),
        ),
        "NZ-OTA": (
            Entity("Otago", "NZ-OTA", "REGION", "en", ""),
            Entity("Ō Tākou", "NZ-OTA", "REGION", "mi", ""),
        ),
        "NZ-STL": (
            Entity("Southland", "NZ-STL", "REGION", "en", ""),
            Entity("Te Taiao Tonga", "NZ-STL", "REGION", "mi", ""),
        ),
        "NZ-TAS": (
            Entity("Tasman", "NZ-TAS", "REGION", "en", ""),
            Entity("Te tai o Aorere", "NZ-TAS", "REGION", "mi", ""),
        ),
        "NZ-TKI": (
            Entity("Taranaki", "NZ-TKI", "REGION", "en", ""),
            Entity("Taranaki", "NZ-TKI", "REGION", "mi", ""),
        ),
        "NZ-WGN": (
            Entity("Greater Wellington", "NZ-WGN", "REGION", "en", ""),
            Entity("Te Pane Matua Taiao", "NZ-WGN", "REGION", "mi", ""),
        ),
        "NZ-WKO": (
            Entity("Waikato", "NZ-WKO", "REGION", "en", ""),
            Entity("Waikato", "NZ-WKO", "REGION", "mi", ""),
        ),
        "NZ-WTC": (
            Entity("Te Tai o Poutini", "NZ-WTC", "REGION", "mi", ""),
            Entity("West Coast", "NZ-WTC", "REGION", "en", ""),
        ),
    }
