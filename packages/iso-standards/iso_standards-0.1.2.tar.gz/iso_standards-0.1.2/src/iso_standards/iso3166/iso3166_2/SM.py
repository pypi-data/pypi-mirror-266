"""ISO 3166-2 SM standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SM
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SM-01": (Entity("Acquaviva", "SM-01", "MUNICIPALITY", "it", ""),),
        "SM-02": (Entity("Chiesanuova", "SM-02", "MUNICIPALITY", "it", ""),),
        "SM-03": (Entity("Domagnano", "SM-03", "MUNICIPALITY", "it", ""),),
        "SM-04": (Entity("Faetano", "SM-04", "MUNICIPALITY", "it", ""),),
        "SM-05": (Entity("Fiorentino", "SM-05", "MUNICIPALITY", "it", ""),),
        "SM-06": (Entity("Borgo Maggiore", "SM-06", "MUNICIPALITY", "it", ""),),
        "SM-07": (Entity("Città di San Marino", "SM-07", "MUNICIPALITY", "it", ""),),
        "SM-08": (Entity("Montegiardino", "SM-08", "MUNICIPALITY", "it", ""),),
        "SM-09": (Entity("Serravalle", "SM-09", "MUNICIPALITY", "it", ""),),
    }
