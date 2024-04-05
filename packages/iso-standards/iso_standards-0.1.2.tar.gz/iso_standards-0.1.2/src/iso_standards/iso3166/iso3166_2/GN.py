"""ISO 3166-2 GN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GN-B": (Entity("Boké", "GN-B", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-BE": (Entity("Beyla", "GN-BE", "PREFECTURE", "fr", "GN-N"),),
        "GN-BF": (Entity("Boffa", "GN-BF", "PREFECTURE", "fr", "GN-B"),),
        "GN-BK": (Entity("Boké", "GN-BK", "PREFECTURE", "fr", "GN-B"),),
        "GN-C": (Entity("Conakry", "GN-C", "GOVERNORATE", "fr", ""),),
        "GN-CO": (Entity("Coyah", "GN-CO", "PREFECTURE", "fr", "GN-D"),),
        "GN-D": (Entity("Kindia", "GN-D", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-DB": (Entity("Dabola", "GN-DB", "PREFECTURE", "fr", "GN-F"),),
        "GN-DI": (Entity("Dinguiraye", "GN-DI", "PREFECTURE", "fr", "GN-F"),),
        "GN-DL": (Entity("Dalaba", "GN-DL", "PREFECTURE", "fr", "GN-M"),),
        "GN-DU": (Entity("Dubréka", "GN-DU", "PREFECTURE", "fr", "GN-D"),),
        "GN-F": (Entity("Faranah", "GN-F", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-FA": (Entity("Faranah", "GN-FA", "PREFECTURE", "fr", "GN-F"),),
        "GN-FO": (Entity("Forécariah", "GN-FO", "PREFECTURE", "fr", "GN-D"),),
        "GN-FR": (Entity("Fria", "GN-FR", "PREFECTURE", "fr", "GN-B"),),
        "GN-GA": (Entity("Gaoual", "GN-GA", "PREFECTURE", "fr", "GN-B"),),
        "GN-GU": (Entity("Guékédou", "GN-GU", "PREFECTURE", "fr", "GN-N"),),
        "GN-K": (Entity("Kankan", "GN-K", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-KA": (Entity("Kankan", "GN-KA", "PREFECTURE", "fr", "GN-K"),),
        "GN-KB": (Entity("Koubia", "GN-KB", "PREFECTURE", "fr", "GN-L"),),
        "GN-KD": (Entity("Kindia", "GN-KD", "PREFECTURE", "fr", "GN-D"),),
        "GN-KE": (Entity("Kérouané", "GN-KE", "PREFECTURE", "fr", "GN-K"),),
        "GN-KN": (Entity("Koundara", "GN-KN", "PREFECTURE", "fr", "GN-B"),),
        "GN-KO": (Entity("Kouroussa", "GN-KO", "PREFECTURE", "fr", "GN-K"),),
        "GN-KS": (Entity("Kissidougou", "GN-KS", "PREFECTURE", "fr", "GN-F"),),
        "GN-L": (Entity("Labé", "GN-L", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-LA": (Entity("Labé", "GN-LA", "PREFECTURE", "fr", "GN-L"),),
        "GN-LE": (Entity("Lélouma", "GN-LE", "PREFECTURE", "fr", "GN-L"),),
        "GN-LO": (Entity("Lola", "GN-LO", "PREFECTURE", "fr", "GN-N"),),
        "GN-M": (Entity("Mamou", "GN-M", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-MC": (Entity("Macenta", "GN-MC", "PREFECTURE", "fr", "GN-N"),),
        "GN-MD": (Entity("Mandiana", "GN-MD", "PREFECTURE", "fr", "GN-K"),),
        "GN-ML": (Entity("Mali", "GN-ML", "PREFECTURE", "fr", "GN-L"),),
        "GN-MM": (Entity("Mamou", "GN-MM", "PREFECTURE", "fr", "GN-M"),),
        "GN-N": (Entity("Nzérékoré", "GN-N", "ADMINISTRATIVE REGION", "fr", ""),),
        "GN-NZ": (Entity("Nzérékoré", "GN-NZ", "PREFECTURE", "fr", "GN-N"),),
        "GN-PI": (Entity("Pita", "GN-PI", "PREFECTURE", "fr", "GN-M"),),
        "GN-SI": (Entity("Siguiri", "GN-SI", "PREFECTURE", "fr", "GN-K"),),
        "GN-TE": (Entity("Télimélé", "GN-TE", "PREFECTURE", "fr", "GN-D"),),
        "GN-TO": (Entity("Tougué", "GN-TO", "PREFECTURE", "fr", "GN-L"),),
        "GN-YO": (Entity("Yomou", "GN-YO", "PREFECTURE", "fr", "GN-N"),),
    }
