"""ISO 3166-2 DO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:DO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "DO-01": (Entity("Distrito Nacional", "DO-01", "DISTRICT", "es", "DO-40"),),
        "DO-02": (Entity("Azua", "DO-02", "PROVINCE", "es", "DO-41"),),
        "DO-03": (Entity("Baoruco", "DO-03", "PROVINCE", "es", "DO-38"),),
        "DO-04": (Entity("Barahona", "DO-04", "PROVINCE", "es", "DO-38"),),
        "DO-05": (Entity("Dajabón", "DO-05", "PROVINCE", "es", "DO-34"),),
        "DO-06": (Entity("Duarte", "DO-06", "PROVINCE", "es", "DO-33"),),
        "DO-07": (Entity("Elías Piña", "DO-07", "PROVINCE", "es", "DO-37"),),
        "DO-08": (Entity("El Seibo", "DO-08", "PROVINCE", "es", "DO-42"),),
        "DO-09": (Entity("Espaillat", "DO-09", "PROVINCE", "es", "DO-35"),),
        "DO-10": (Entity("Independencia", "DO-10", "PROVINCE", "es", "DO-38"),),
        "DO-11": (Entity("La Altagracia", "DO-11", "PROVINCE", "es", "DO-42"),),
        "DO-12": (Entity("La Romana", "DO-12", "PROVINCE", "es", "DO-42"),),
        "DO-13": (Entity("La Vega", "DO-13", "PROVINCE", "es", "DO-36"),),
        "DO-14": (Entity("María Trinidad Sánchez", "DO-14", "PROVINCE", "es", "DO-33"),),
        "DO-15": (Entity("Monte Cristi", "DO-15", "PROVINCE", "es", "DO-34"),),
        "DO-16": (Entity("Pedernales", "DO-16", "PROVINCE", "es", "DO-38"),),
        "DO-17": (Entity("Peravia", "DO-17", "PROVINCE", "es", "DO-41"),),
        "DO-18": (Entity("Puerto Plata", "DO-18", "PROVINCE", "es", "DO-35"),),
        "DO-19": (Entity("Hermanas Mirabal", "DO-19", "PROVINCE", "es", "DO-33"),),
        "DO-20": (Entity("Samaná", "DO-20", "PROVINCE", "es", "DO-33"),),
        "DO-21": (Entity("San Cristóbal", "DO-21", "PROVINCE", "es", "DO-41"),),
        "DO-22": (Entity("San Juan", "DO-22", "PROVINCE", "es", "DO-37"),),
        "DO-23": (Entity("San Pedro de Macorís", "DO-23", "PROVINCE", "es", "DO-39"),),
        "DO-24": (Entity("Sánchez Ramírez", "DO-24", "PROVINCE", "es", "DO-36"),),
        "DO-25": (Entity("Santiago", "DO-25", "PROVINCE", "es", "DO-35"),),
        "DO-26": (Entity("Santiago Rodríguez", "DO-26", "PROVINCE", "es", "DO-34"),),
        "DO-27": (Entity("Valverde", "DO-27", "PROVINCE", "es", "DO-34"),),
        "DO-28": (Entity("Monseñor Nouel", "DO-28", "PROVINCE", "es", "DO-36"),),
        "DO-29": (Entity("Monte Plata", "DO-29", "PROVINCE", "es", "DO-39"),),
        "DO-30": (Entity("Hato Mayor", "DO-30", "PROVINCE", "es", "DO-39"),),
        "DO-31": (Entity("San José de Ocoa", "DO-31", "PROVINCE", "es", "DO-41"),),
        "DO-32": (Entity("Santo Domingo", "DO-32", "PROVINCE", "es", "DO-40"),),
        "DO-33": (Entity("Cibao Nordeste", "DO-33", "REGION", "es", ""),),
        "DO-34": (Entity("Cibao Noroeste", "DO-34", "REGION", "es", ""),),
        "DO-35": (Entity("Cibao Norte", "DO-35", "REGION", "es", ""),),
        "DO-36": (Entity("Cibao Sur", "DO-36", "REGION", "es", ""),),
        "DO-37": (Entity("El Valle", "DO-37", "REGION", "es", ""),),
        "DO-38": (Entity("Enriquillo", "DO-38", "REGION", "es", ""),),
        "DO-39": (Entity("Higuamo", "DO-39", "REGION", "es", ""),),
        "DO-40": (Entity("Ozama", "DO-40", "REGION", "es", ""),),
        "DO-41": (Entity("Valdesia", "DO-41", "REGION", "es", ""),),
        "DO-42": (Entity("Yuma", "DO-42", "REGION", "es", ""),),
    }
