"""ISO 3166-2 MH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MH-ALK": (
            Entity("Aelok", "MH-ALK", "MUNICIPALITY", "mh", "MH-T"),
            Entity("Ailuk", "MH-ALK", "MUNICIPALITY", "en", "MH-T"),
        ),
        "MH-ALL": (
            Entity("Aelōn̄ḷapḷap", "MH-ALL", "MUNICIPALITY", "mh", "MH-L"),
            Entity("Ailinglaplap", "MH-ALL", "MUNICIPALITY", "en", "MH-L"),
        ),
        "MH-ARN": (
            Entity("Arno", "MH-ARN", "MUNICIPALITY", "en", "MH-T"),
            Entity("Arṇo", "MH-ARN", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-AUR": (
            Entity("Aur", "MH-AUR", "MUNICIPALITY", "en", "MH-T"),
            Entity("Aur", "MH-AUR", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-EBO": (
            Entity("Ebon", "MH-EBO", "MUNICIPALITY", "en", "MH-L"),
            Entity("Epoon", "MH-EBO", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-ENI": (
            Entity("Enewetak & Ujelang", "MH-ENI", "MUNICIPALITY", "en", "MH-L"),
            Entity("Ānewetak & Wūjlan̄", "MH-ENI", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-JAB": (
            Entity("Jabat", "MH-JAB", "MUNICIPALITY", "en", "MH-L"),
            Entity("Jebat", "MH-JAB", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-JAL": (
            Entity("Jaluit", "MH-JAL", "MUNICIPALITY", "en", "MH-L"),
            Entity("Jālwōj", "MH-JAL", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-KIL": (
            Entity("Bikini & Kili", "MH-KIL", "MUNICIPALITY", "en", "MH-L"),
            Entity("Pikinni & Kōle", "MH-KIL", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-KWA": (
            Entity("Kuwajleen", "MH-KWA", "MUNICIPALITY", "mh", "MH-L"),
            Entity("Kwajalein", "MH-KWA", "MUNICIPALITY", "en", "MH-L"),
        ),
        "MH-L": (
            Entity("Ralik chain", "MH-L", "CHAIN (OF ISLANDS)", "en", ""),
            Entity("Ralik chain", "MH-L", "CHAIN (OF ISLANDS)", "mh", ""),
        ),
        "MH-LAE": (
            Entity("Lae", "MH-LAE", "MUNICIPALITY", "en", "MH-L"),
            Entity("Lae", "MH-LAE", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-LIB": (
            Entity("Ellep", "MH-LIB", "MUNICIPALITY", "mh", "MH-L"),
            Entity("Lib", "MH-LIB", "MUNICIPALITY", "en", "MH-L"),
        ),
        "MH-LIK": (
            Entity("Likiep", "MH-LIK", "MUNICIPALITY", "en", "MH-T"),
            Entity("Likiep", "MH-LIK", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-MAJ": (
            Entity("Majuro", "MH-MAJ", "MUNICIPALITY", "en", "MH-T"),
            Entity("Mājro", "MH-MAJ", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-MAL": (
            Entity("Maloelap", "MH-MAL", "MUNICIPALITY", "en", "MH-T"),
            Entity("Ṃaḷoeḷap", "MH-MAL", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-MEJ": (
            Entity("Mejit", "MH-MEJ", "MUNICIPALITY", "en", "MH-T"),
            Entity("Mājej", "MH-MEJ", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-MIL": (
            Entity("Mile", "MH-MIL", "MUNICIPALITY", "mh", "MH-T"),
            Entity("Mili", "MH-MIL", "MUNICIPALITY", "en", "MH-T"),
        ),
        "MH-NMK": (
            Entity("Namdrik", "MH-NMK", "MUNICIPALITY", "en", "MH-L"),
            Entity("Naṃdik", "MH-NMK", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-NMU": (
            Entity("Namu", "MH-NMU", "MUNICIPALITY", "en", "MH-L"),
            Entity("Naṃo", "MH-NMU", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-RON": (
            Entity("Rongelap", "MH-RON", "MUNICIPALITY", "en", "MH-L"),
            Entity("Ron̄ḷap", "MH-RON", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-T": (
            Entity("Ratak chain", "MH-T", "CHAIN (OF ISLANDS)", "en", ""),
            Entity("Ratak chain", "MH-T", "CHAIN (OF ISLANDS)", "mh", ""),
        ),
        "MH-UJA": (
            Entity("Ujae", "MH-UJA", "MUNICIPALITY", "en", "MH-L"),
            Entity("Ujae", "MH-UJA", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-UTI": (
            Entity("Utrik", "MH-UTI", "MUNICIPALITY", "en", "MH-T"),
            Entity("Utrōk", "MH-UTI", "MUNICIPALITY", "mh", "MH-T"),
        ),
        "MH-WTH": (
            Entity("Wotho", "MH-WTH", "MUNICIPALITY", "en", "MH-L"),
            Entity("Wōtto", "MH-WTH", "MUNICIPALITY", "mh", "MH-L"),
        ),
        "MH-WTJ": (
            Entity("Wotje", "MH-WTJ", "MUNICIPALITY", "en", "MH-T"),
            Entity("Wōjjā", "MH-WTJ", "MUNICIPALITY", "mh", "MH-T"),
        ),
    }
