"""ISO 3166-2 CO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CO-AMA": (Entity("Amazonas", "CO-AMA", "DEPARTMENT", "es", ""),),
        "CO-ANT": (Entity("Antioquia", "CO-ANT", "DEPARTMENT", "es", ""),),
        "CO-ARA": (Entity("Arauca", "CO-ARA", "DEPARTMENT", "es", ""),),
        "CO-ATL": (Entity("Atlántico", "CO-ATL", "DEPARTMENT", "es", ""),),
        "CO-BOL": (Entity("Bolívar", "CO-BOL", "DEPARTMENT", "es", ""),),
        "CO-BOY": (Entity("Boyacá", "CO-BOY", "DEPARTMENT", "es", ""),),
        "CO-CAL": (Entity("Caldas", "CO-CAL", "DEPARTMENT", "es", ""),),
        "CO-CAQ": (Entity("Caquetá", "CO-CAQ", "DEPARTMENT", "es", ""),),
        "CO-CAS": (Entity("Casanare", "CO-CAS", "DEPARTMENT", "es", ""),),
        "CO-CAU": (Entity("Cauca", "CO-CAU", "DEPARTMENT", "es", ""),),
        "CO-CES": (Entity("Cesar", "CO-CES", "DEPARTMENT", "es", ""),),
        "CO-CHO": (Entity("Chocó", "CO-CHO", "DEPARTMENT", "es", ""),),
        "CO-COR": (Entity("Córdoba", "CO-COR", "DEPARTMENT", "es", ""),),
        "CO-CUN": (Entity("Cundinamarca", "CO-CUN", "DEPARTMENT", "es", ""),),
        "CO-DC": (Entity("Distrito Capital de Bogotá", "CO-DC", "CAPITAL DISTRICT", "es", ""),),
        "CO-GUA": (Entity("Guainía", "CO-GUA", "DEPARTMENT", "es", ""),),
        "CO-GUV": (Entity("Guaviare", "CO-GUV", "DEPARTMENT", "es", ""),),
        "CO-HUI": (Entity("Huila", "CO-HUI", "DEPARTMENT", "es", ""),),
        "CO-LAG": (Entity("La Guajira", "CO-LAG", "DEPARTMENT", "es", ""),),
        "CO-MAG": (Entity("Magdalena", "CO-MAG", "DEPARTMENT", "es", ""),),
        "CO-MET": (Entity("Meta", "CO-MET", "DEPARTMENT", "es", ""),),
        "CO-NAR": (Entity("Nariño", "CO-NAR", "DEPARTMENT", "es", ""),),
        "CO-NSA": (Entity("Norte de Santander", "CO-NSA", "DEPARTMENT", "es", ""),),
        "CO-PUT": (Entity("Putumayo", "CO-PUT", "DEPARTMENT", "es", ""),),
        "CO-QUI": (Entity("Quindío", "CO-QUI", "DEPARTMENT", "es", ""),),
        "CO-RIS": (Entity("Risaralda", "CO-RIS", "DEPARTMENT", "es", ""),),
        "CO-SAN": (Entity("Santander", "CO-SAN", "DEPARTMENT", "es", ""),),
        "CO-SAP": (Entity("San Andrés", "CO-SAP", "DEPARTMENT", "es", ""),),
        "CO-SUC": (Entity("Sucre", "CO-SUC", "DEPARTMENT", "es", ""),),
        "CO-TOL": (Entity("Tolima", "CO-TOL", "DEPARTMENT", "es", ""),),
        "CO-VAC": (Entity("Valle del Cauca", "CO-VAC", "DEPARTMENT", "es", ""),),
        "CO-VAU": (Entity("Vaupés", "CO-VAU", "DEPARTMENT", "es", ""),),
        "CO-VID": (Entity("Vichada", "CO-VID", "DEPARTMENT", "es", ""),),
    }
