"""ISO 3166-2 UA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:UA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "UA-05": (Entity("Vinnytska oblast", "UA-05", "REGION", "uk", ""),),
        "UA-07": (Entity("Volynska oblast", "UA-07", "REGION", "uk", ""),),
        "UA-09": (Entity("Luhanska oblast", "UA-09", "REGION", "uk", ""),),
        "UA-12": (Entity("Dnipropetrovska oblast", "UA-12", "REGION", "uk", ""),),
        "UA-14": (Entity("Donetska oblast", "UA-14", "REGION", "uk", ""),),
        "UA-18": (Entity("Zhytomyrska oblast", "UA-18", "REGION", "uk", ""),),
        "UA-21": (Entity("Zakarpatska oblast", "UA-21", "REGION", "uk", ""),),
        "UA-23": (Entity("Zaporizka oblast", "UA-23", "REGION", "uk", ""),),
        "UA-26": (Entity("Ivano-Frankivska oblast", "UA-26", "REGION", "uk", ""),),
        "UA-30": (Entity("Kyiv", "UA-30", "CITY", "uk", ""),),
        "UA-32": (Entity("Kyivska oblast", "UA-32", "REGION", "uk", ""),),
        "UA-35": (Entity("Kirovohradska oblast", "UA-35", "REGION", "uk", ""),),
        "UA-40": (Entity("Sevastopol", "UA-40", "CITY", "uk", ""),),
        "UA-43": (Entity("Avtonomna Respublika Krym", "UA-43", "REPUBLIC", "uk", ""),),
        "UA-46": (Entity("Lvivska oblast", "UA-46", "REGION", "uk", ""),),
        "UA-48": (Entity("Mykolaivska oblast", "UA-48", "REGION", "uk", ""),),
        "UA-51": (Entity("Odeska oblast", "UA-51", "REGION", "uk", ""),),
        "UA-53": (Entity("Poltavska oblast", "UA-53", "REGION", "uk", ""),),
        "UA-56": (Entity("Rivnenska oblast", "UA-56", "REGION", "uk", ""),),
        "UA-59": (Entity("Sumska oblast", "UA-59", "REGION", "uk", ""),),
        "UA-61": (Entity("Ternopilska oblast", "UA-61", "REGION", "uk", ""),),
        "UA-63": (Entity("Kharkivska oblast", "UA-63", "REGION", "uk", ""),),
        "UA-65": (Entity("Khersonska oblast", "UA-65", "REGION", "uk", ""),),
        "UA-68": (Entity("Khmelnytska oblast", "UA-68", "REGION", "uk", ""),),
        "UA-71": (Entity("Cherkaska oblast", "UA-71", "REGION", "uk", ""),),
        "UA-74": (Entity("Chernihivska oblast", "UA-74", "REGION", "uk", ""),),
        "UA-77": (Entity("Chernivetska oblast", "UA-77", "REGION", "uk", ""),),
    }
