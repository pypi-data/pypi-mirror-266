"""ISO 3166-2 MU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MU-AG": (Entity("Agalega Islands", "MU-AG", "DEPENDENCY", "en", ""),),
        "MU-BL": (Entity("Black River", "MU-BL", "DISTRICT", "en", ""),),
        "MU-CC": (Entity("Cargados Carajos Shoals", "MU-CC", "DEPENDENCY", "en", ""),),
        "MU-FL": (Entity("Flacq", "MU-FL", "DISTRICT", "en", ""),),
        "MU-GP": (Entity("Grand Port", "MU-GP", "DISTRICT", "en", ""),),
        "MU-MO": (Entity("Moka", "MU-MO", "DISTRICT", "en", ""),),
        "MU-PA": (Entity("Pamplemousses", "MU-PA", "DISTRICT", "en", ""),),
        "MU-PL": (Entity("Port Louis", "MU-PL", "DISTRICT", "en", ""),),
        "MU-PW": (Entity("Plaines Wilhems", "MU-PW", "DISTRICT", "en", ""),),
        "MU-RO": (Entity("Rodrigues Island", "MU-RO", "DEPENDENCY", "en", ""),),
        "MU-RR": (Entity("Rivière du Rempart", "MU-RR", "DISTRICT", "en", ""),),
        "MU-SA": (Entity("Savanne", "MU-SA", "DISTRICT", "en", ""),),
    }
