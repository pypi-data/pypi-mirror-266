"""ISO 3166-2 GL standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:GL
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "GL-AV": (Entity("Avannaata Kommunia", "GL-AV", "MUNICIPALITY", "kl", ""),),
        "GL-KU": (Entity("Kommune Kujalleq", "GL-KU", "MUNICIPALITY", "kl", ""),),
        "GL-QE": (Entity("Qeqqata Kommunia", "GL-QE", "MUNICIPALITY", "kl", ""),),
        "GL-QT": (Entity("Kommune Qeqertalik", "GL-QT", "MUNICIPALITY", "kl", ""),),
        "GL-SM": (Entity("Kommuneqarfik Sermersooq", "GL-SM", "MUNICIPALITY", "kl", ""),),
    }
