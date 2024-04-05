"""ISO 3166-2 CF standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CF
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CF-AC": (
            Entity("Ouham", "CF-AC", "PREFECTURE", "fr", ""),
            Entity("Wâmo", "CF-AC", "PREFECTURE", "sg", ""),
        ),
        "CF-BB": (
            Entity("Bamingui-Bangoran", "CF-BB", "PREFECTURE", "fr", ""),
            Entity("Bamïngï-Bangoran", "CF-BB", "PREFECTURE", "sg", ""),
        ),
        "CF-BGF": (
            Entity("Bangui", "CF-BGF", "COMMUNE", "fr", ""),
            Entity("Bangî", "CF-BGF", "COMMUNE", "sg", ""),
        ),
        "CF-BK": (
            Entity("Basse-Kotto", "CF-BK", "PREFECTURE", "fr", ""),
            Entity("Do-Kötö", "CF-BK", "PREFECTURE", "sg", ""),
        ),
        "CF-HK": (
            Entity("Haute-Kotto", "CF-HK", "PREFECTURE", "fr", ""),
            Entity("Tö-Kötö", "CF-HK", "PREFECTURE", "sg", ""),
        ),
        "CF-HM": (
            Entity("Haut-Mbomou", "CF-HM", "PREFECTURE", "fr", ""),
            Entity("Tö-Mbömü", "CF-HM", "PREFECTURE", "sg", ""),
        ),
        "CF-HS": (
            Entity("Haute-Sangha / Mambéré-Kadéï", "CF-HS", "PREFECTURE", "fr", ""),
            Entity("Tö-Sangä / Mbaere-Kadeï", "CF-HS", "PREFECTURE", "sg", ""),
        ),
        "CF-KB": (
            Entity("Gribingui", "CF-KB", "ECONOMIC PREFECTURE", "fr", ""),
            Entity("Gïrïbïngï", "CF-KB", "ECONOMIC PREFECTURE", "sg", ""),
        ),
        "CF-KG": (
            Entity("Kemö-Gïrïbïngï", "CF-KG", "PREFECTURE", "sg", ""),
            Entity("Kémo-Gribingui", "CF-KG", "PREFECTURE", "fr", ""),
        ),
        "CF-LB": (
            Entity("Lobaye", "CF-LB", "PREFECTURE", "fr", ""),
            Entity("Lobâye", "CF-LB", "PREFECTURE", "sg", ""),
        ),
        "CF-MB": (
            Entity("Mbomou", "CF-MB", "PREFECTURE", "fr", ""),
            Entity("Mbömü", "CF-MB", "PREFECTURE", "sg", ""),
        ),
        "CF-MP": (
            Entity("Ombella-Mpoko", "CF-MP", "PREFECTURE", "fr", ""),
            Entity("Ömbëlä-Pökö", "CF-MP", "PREFECTURE", "sg", ""),
        ),
        "CF-NM": (
            Entity("Nana-Mambéré", "CF-NM", "PREFECTURE", "fr", ""),
            Entity("Nanä-Mbaere", "CF-NM", "PREFECTURE", "sg", ""),
        ),
        "CF-OP": (
            Entity("Ouham-Pendé", "CF-OP", "PREFECTURE", "fr", ""),
            Entity("Wâmo-Pendë", "CF-OP", "PREFECTURE", "sg", ""),
        ),
        "CF-SE": (
            Entity("Sangha", "CF-SE", "ECONOMIC PREFECTURE", "fr", ""),
            Entity("Sangä", "CF-SE", "ECONOMIC PREFECTURE", "sg", ""),
        ),
        "CF-UK": (
            Entity("Ouaka", "CF-UK", "PREFECTURE", "fr", ""),
            Entity("Wäkä", "CF-UK", "PREFECTURE", "sg", ""),
        ),
        "CF-VK": (
            Entity("Vakaga", "CF-VK", "PREFECTURE", "fr", ""),
            Entity("Vakaga", "CF-VK", "PREFECTURE", "sg", ""),
        ),
    }
