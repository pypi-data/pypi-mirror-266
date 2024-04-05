"""ISO 3166-2 TT standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TT
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TT-ARI": (Entity("Arima", "TT-ARI", "BOROUGH", "en", ""),),
        "TT-CHA": (Entity("Chaguanas", "TT-CHA", "BOROUGH", "en", ""),),
        "TT-CTT": (Entity("Couva-Tabaquite-Talparo", "TT-CTT", "REGION", "en", ""),),
        "TT-DMN": (Entity("Diego Martin", "TT-DMN", "REGION", "en", ""),),
        "TT-MRC": (Entity("Mayaro-Rio Claro", "TT-MRC", "REGION", "en", ""),),
        "TT-PED": (Entity("Penal-Debe", "TT-PED", "REGION", "en", ""),),
        "TT-POS": (Entity("Port of Spain", "TT-POS", "CITY", "en", ""),),
        "TT-PRT": (Entity("Princes Town", "TT-PRT", "REGION", "en", ""),),
        "TT-PTF": (Entity("Point Fortin", "TT-PTF", "BOROUGH", "en", ""),),
        "TT-SFO": (Entity("San Fernando", "TT-SFO", "CITY", "en", ""),),
        "TT-SGE": (Entity("Sangre Grande", "TT-SGE", "REGION", "en", ""),),
        "TT-SIP": (Entity("Siparia", "TT-SIP", "REGION", "en", ""),),
        "TT-SJL": (Entity("San Juan-Laventille", "TT-SJL", "REGION", "en", ""),),
        "TT-TOB": (Entity("Tobago", "TT-TOB", "WARD", "en", ""),),
        "TT-TUP": (Entity("Tunapuna-Piarco", "TT-TUP", "REGION", "en", ""),),
    }
