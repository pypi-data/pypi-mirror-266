"""ISO 3166-2 KP standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KP
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KP-01": (
            Entity("P'yǒngyang", "KP-01", "CAPITAL CITY", "ko", ""),
            Entity("Phyeongyang", "KP-01", "CAPITAL CITY", "ko", ""),
        ),
        "KP-02": (
            Entity("P'yǒngan-namdo", "KP-02", "PROVINCE", "ko", ""),
            Entity("Phyeongannamto", "KP-02", "PROVINCE", "ko", ""),
        ),
        "KP-03": (
            Entity("P'yǒngan-bukto", "KP-03", "PROVINCE", "ko", ""),
            Entity("Phyeonganpukto", "KP-03", "PROVINCE", "ko", ""),
        ),
        "KP-04": (
            Entity("Chagang-do", "KP-04", "PROVINCE", "ko", ""),
            Entity("Jakangto", "KP-04", "PROVINCE", "ko", ""),
        ),
        "KP-05": (
            Entity("Hwanghae-namdo", "KP-05", "PROVINCE", "ko", ""),
            Entity("Hwanghainamto", "KP-05", "PROVINCE", "ko", ""),
        ),
        "KP-06": (
            Entity("Hwanghae-bukto", "KP-06", "PROVINCE", "ko", ""),
            Entity("Hwanghaipukto", "KP-06", "PROVINCE", "ko", ""),
        ),
        "KP-07": (
            Entity("Kangweonto", "KP-07", "PROVINCE", "ko", ""),
            Entity("Kangwǒn-do", "KP-07", "PROVINCE", "ko", ""),
        ),
        "KP-08": (
            Entity("Hamgyǒng-namdo", "KP-08", "PROVINCE", "ko", ""),
            Entity("Hamkyeongnamto", "KP-08", "PROVINCE", "ko", ""),
        ),
        "KP-09": (
            Entity("Hamgyǒng-bukto", "KP-09", "PROVINCE", "ko", ""),
            Entity("Hamkyeongpukto", "KP-09", "PROVINCE", "ko", ""),
        ),
        "KP-10": (
            Entity("Ryanggang-do", "KP-10", "PROVINCE", "ko", ""),
            Entity("Ryangkangto", "KP-10", "PROVINCE", "ko", ""),
        ),
        "KP-13": (
            Entity("Raseon", "KP-13", "SPECIAL CITY", "ko", ""),
            Entity("Rasǒn", "KP-13", "SPECIAL CITY", "ko", ""),
        ),
        "KP-14": (
            Entity("Nampho", "KP-14", "METROPOLITAN CITY", "ko", ""),
            Entity("Namp’o", "KP-14", "METROPOLITAN CITY", "ko", ""),
        ),
        "KP-15": (
            Entity("Kaeseong", "KP-15", "METROPOLITAN CITY", "ko", ""),
            Entity("Kaesŏng", "KP-15", "METROPOLITAN CITY", "ko", ""),
        ),
    }
