"""ISO 3166-2 HU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:HU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "HU-BA": (Entity("Baranya", "HU-BA", "COUNTY", "hu", ""),),
        "HU-BC": (Entity("Békéscsaba", "HU-BC", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-BE": (Entity("Békés", "HU-BE", "COUNTY", "hu", ""),),
        "HU-BK": (Entity("Bács-Kiskun", "HU-BK", "COUNTY", "hu", ""),),
        "HU-BU": (Entity("Budapest", "HU-BU", "CAPITAL CITY", "hu", ""),),
        "HU-BZ": (Entity("Borsod-Abaúj-Zemplén", "HU-BZ", "COUNTY", "hu", ""),),
        "HU-CS": (Entity("Csongrád-Csanád", "HU-CS", "COUNTY", "hu", ""),),
        "HU-DE": (Entity("Debrecen", "HU-DE", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-DU": (Entity("Dunaújváros", "HU-DU", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-EG": (Entity("Eger", "HU-EG", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-ER": (Entity("Érd", "HU-ER", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-FE": (Entity("Fejér", "HU-FE", "COUNTY", "hu", ""),),
        "HU-GS": (Entity("Győr-Moson-Sopron", "HU-GS", "COUNTY", "hu", ""),),
        "HU-GY": (Entity("Győr", "HU-GY", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-HB": (Entity("Hajdú-Bihar", "HU-HB", "COUNTY", "hu", ""),),
        "HU-HE": (Entity("Heves", "HU-HE", "COUNTY", "hu", ""),),
        "HU-HV": (Entity("Hódmezővásárhely", "HU-HV", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-JN": (Entity("Jász-Nagykun-Szolnok", "HU-JN", "COUNTY", "hu", ""),),
        "HU-KE": (Entity("Komárom-Esztergom", "HU-KE", "COUNTY", "hu", ""),),
        "HU-KM": (Entity("Kecskemét", "HU-KM", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-KV": (Entity("Kaposvár", "HU-KV", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-MI": (Entity("Miskolc", "HU-MI", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-NK": (Entity("Nagykanizsa", "HU-NK", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-NO": (Entity("Nógrád", "HU-NO", "COUNTY", "hu", ""),),
        "HU-NY": (Entity("Nyíregyháza", "HU-NY", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-PE": (Entity("Pest", "HU-PE", "COUNTY", "hu", ""),),
        "HU-PS": (Entity("Pécs", "HU-PS", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SD": (Entity("Szeged", "HU-SD", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SF": (Entity("Székesfehérvár", "HU-SF", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SH": (Entity("Szombathely", "HU-SH", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SK": (Entity("Szolnok", "HU-SK", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SN": (Entity("Sopron", "HU-SN", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SO": (Entity("Somogy", "HU-SO", "COUNTY", "hu", ""),),
        "HU-SS": (Entity("Szekszárd", "HU-SS", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-ST": (Entity("Salgótarján", "HU-ST", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-SZ": (Entity("Szabolcs-Szatmár-Bereg", "HU-SZ", "COUNTY", "hu", ""),),
        "HU-TB": (Entity("Tatabánya", "HU-TB", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-TO": (Entity("Tolna", "HU-TO", "COUNTY", "hu", ""),),
        "HU-VA": (Entity("Vas", "HU-VA", "COUNTY", "hu", ""),),
        "HU-VE": (Entity("Veszprém", "HU-VE", "COUNTY", "hu", ""),),
        "HU-VM": (Entity("Veszprém", "HU-VM", "CITY WITH COUNTY RIGHTS", "hu", ""),),
        "HU-ZA": (Entity("Zala", "HU-ZA", "COUNTY", "hu", ""),),
        "HU-ZE": (Entity("Zalaegerszeg", "HU-ZE", "CITY WITH COUNTY RIGHTS", "hu", ""),),
    }
