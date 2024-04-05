"""ISO 3166-2 MX standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MX
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MX-AGU": (Entity("Aguascalientes", "MX-AGU", "STATE", "es", ""),),
        "MX-BCN": (Entity("Baja California", "MX-BCN", "STATE", "es", ""),),
        "MX-BCS": (Entity("Baja California Sur", "MX-BCS", "STATE", "es", ""),),
        "MX-CAM": (Entity("Campeche", "MX-CAM", "STATE", "es", ""),),
        "MX-CHH": (Entity("Chihuahua", "MX-CHH", "STATE", "es", ""),),
        "MX-CHP": (Entity("Chiapas", "MX-CHP", "STATE", "es", ""),),
        "MX-CMX": (Entity("Ciudad de México", "MX-CMX", "FEDERAL ENTITY", "es", ""),),
        "MX-COA": (Entity("Coahuila de Zaragoza", "MX-COA", "STATE", "es", ""),),
        "MX-COL": (Entity("Colima", "MX-COL", "STATE", "es", ""),),
        "MX-DUR": (Entity("Durango", "MX-DUR", "STATE", "es", ""),),
        "MX-GRO": (Entity("Guerrero", "MX-GRO", "STATE", "es", ""),),
        "MX-GUA": (Entity("Guanajuato", "MX-GUA", "STATE", "es", ""),),
        "MX-HID": (Entity("Hidalgo", "MX-HID", "STATE", "es", ""),),
        "MX-JAL": (Entity("Jalisco", "MX-JAL", "STATE", "es", ""),),
        "MX-MEX": (Entity("México", "MX-MEX", "STATE", "es", ""),),
        "MX-MIC": (Entity("Michoacán de Ocampo", "MX-MIC", "STATE", "es", ""),),
        "MX-MOR": (Entity("Morelos", "MX-MOR", "STATE", "es", ""),),
        "MX-NAY": (Entity("Nayarit", "MX-NAY", "STATE", "es", ""),),
        "MX-NLE": (Entity("Nuevo León", "MX-NLE", "STATE", "es", ""),),
        "MX-OAX": (Entity("Oaxaca", "MX-OAX", "STATE", "es", ""),),
        "MX-PUE": (Entity("Puebla", "MX-PUE", "STATE", "es", ""),),
        "MX-QUE": (Entity("Querétaro", "MX-QUE", "STATE", "es", ""),),
        "MX-ROO": (Entity("Quintana Roo", "MX-ROO", "STATE", "es", ""),),
        "MX-SIN": (Entity("Sinaloa", "MX-SIN", "STATE", "es", ""),),
        "MX-SLP": (Entity("San Luis Potosí", "MX-SLP", "STATE", "es", ""),),
        "MX-SON": (Entity("Sonora", "MX-SON", "STATE", "es", ""),),
        "MX-TAB": (Entity("Tabasco", "MX-TAB", "STATE", "es", ""),),
        "MX-TAM": (Entity("Tamaulipas", "MX-TAM", "STATE", "es", ""),),
        "MX-TLA": (Entity("Tlaxcala", "MX-TLA", "STATE", "es", ""),),
        "MX-VER": (Entity("Veracruz de Ignacio de la Llave", "MX-VER", "STATE", "es", ""),),
        "MX-YUC": (Entity("Yucatán", "MX-YUC", "STATE", "es", ""),),
        "MX-ZAC": (Entity("Zacatecas", "MX-ZAC", "STATE", "es", ""),),
    }
