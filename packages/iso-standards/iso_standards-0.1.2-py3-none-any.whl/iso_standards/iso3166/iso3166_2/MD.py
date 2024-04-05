"""ISO 3166-2 MD standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MD
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MD-AN": (Entity("Anenii Noi", "MD-AN", "DISTRICT", "ro", ""),),
        "MD-BA": (Entity("Bălți", "MD-BA", "CITY", "ro", ""),),
        "MD-BD": (Entity("Bender", "MD-BD", "CITY", "ro", ""),),
        "MD-BR": (Entity("Briceni", "MD-BR", "DISTRICT", "ro", ""),),
        "MD-BS": (Entity("Basarabeasca", "MD-BS", "DISTRICT", "ro", ""),),
        "MD-CA": (Entity("Cahul", "MD-CA", "DISTRICT", "ro", ""),),
        "MD-CL": (Entity("Călărași", "MD-CL", "DISTRICT", "ro", ""),),
        "MD-CM": (Entity("Cimișlia", "MD-CM", "DISTRICT", "ro", ""),),
        "MD-CR": (Entity("Criuleni", "MD-CR", "DISTRICT", "ro", ""),),
        "MD-CS": (Entity("Căușeni", "MD-CS", "DISTRICT", "ro", ""),),
        "MD-CT": (Entity("Cantemir", "MD-CT", "DISTRICT", "ro", ""),),
        "MD-CU": (Entity("Chișinău", "MD-CU", "CITY", "ro", ""),),
        "MD-DO": (Entity("Dondușeni", "MD-DO", "DISTRICT", "ro", ""),),
        "MD-DR": (Entity("Drochia", "MD-DR", "DISTRICT", "ro", ""),),
        "MD-DU": (Entity("Dubăsari", "MD-DU", "DISTRICT", "ro", ""),),
        "MD-ED": (Entity("Edineț", "MD-ED", "DISTRICT", "ro", ""),),
        "MD-FA": (Entity("Fălești", "MD-FA", "DISTRICT", "ro", ""),),
        "MD-FL": (Entity("Florești", "MD-FL", "DISTRICT", "ro", ""),),
        "MD-GA": (Entity("Găgăuzia", "MD-GA", "AUTONOMOUS TERRITORIAL UNIT", "ro", ""),),
        "MD-GL": (Entity("Glodeni", "MD-GL", "DISTRICT", "ro", ""),),
        "MD-HI": (Entity("Hîncești", "MD-HI", "DISTRICT", "ro", ""),),
        "MD-IA": (Entity("Ialoveni", "MD-IA", "DISTRICT", "ro", ""),),
        "MD-LE": (Entity("Leova", "MD-LE", "DISTRICT", "ro", ""),),
        "MD-NI": (Entity("Nisporeni", "MD-NI", "DISTRICT", "ro", ""),),
        "MD-OC": (Entity("Ocnița", "MD-OC", "DISTRICT", "ro", ""),),
        "MD-OR": (Entity("Orhei", "MD-OR", "DISTRICT", "ro", ""),),
        "MD-RE": (Entity("Rezina", "MD-RE", "DISTRICT", "ro", ""),),
        "MD-RI": (Entity("Rîșcani", "MD-RI", "DISTRICT", "ro", ""),),
        "MD-SD": (Entity("Șoldănești", "MD-SD", "DISTRICT", "ro", ""),),
        "MD-SI": (Entity("Sîngerei", "MD-SI", "DISTRICT", "ro", ""),),
        "MD-SN": (Entity("Stînga Nistrului", "MD-SN", "TERRITORIAL UNIT", "ro", ""),),
        "MD-SO": (Entity("Soroca", "MD-SO", "DISTRICT", "ro", ""),),
        "MD-ST": (Entity("Strășeni", "MD-ST", "DISTRICT", "ro", ""),),
        "MD-SV": (Entity("Ștefan Vodă", "MD-SV", "DISTRICT", "ro", ""),),
        "MD-TA": (Entity("Taraclia", "MD-TA", "DISTRICT", "ro", ""),),
        "MD-TE": (Entity("Telenești", "MD-TE", "DISTRICT", "ro", ""),),
        "MD-UN": (Entity("Ungheni", "MD-UN", "DISTRICT", "ro", ""),),
    }
