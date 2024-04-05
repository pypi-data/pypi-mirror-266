"""ISO 3166-2 CV standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CV
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CV-B": (Entity("Ilhas de Barlavento", "CV-B", "GEOGRAPHICAL REGION", "pt", ""),),
        "CV-BR": (Entity("Brava", "CV-BR", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-BV": (Entity("Boa Vista", "CV-BV", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-CA": (Entity("Santa Catarina", "CV-CA", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-CF": (Entity("Santa Catarina do Fogo", "CV-CF", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-CR": (Entity("Santa Cruz", "CV-CR", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-MA": (Entity("Maio", "CV-MA", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-MO": (Entity("Mosteiros", "CV-MO", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-PA": (Entity("Paul", "CV-PA", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-PN": (Entity("Porto Novo", "CV-PN", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-PR": (Entity("Praia", "CV-PR", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-RB": (Entity("Ribeira Brava", "CV-RB", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-RG": (Entity("Ribeira Grande", "CV-RG", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-RS": (Entity("Ribeira Grande de Santiago", "CV-RS", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-S": (Entity("Ilhas de Sotavento", "CV-S", "GEOGRAPHICAL REGION", "pt", ""),),
        "CV-SD": (Entity("São Domingos", "CV-SD", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-SF": (Entity("São Filipe", "CV-SF", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-SL": (Entity("Sal", "CV-SL", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-SM": (Entity("São Miguel", "CV-SM", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-SO": (Entity("São Lourenço dos Órgãos", "CV-SO", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-SS": (Entity("São Salvador do Mundo", "CV-SS", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-SV": (Entity("São Vicente", "CV-SV", "MUNICIPALITY", "pt", "CV-B"),),
        "CV-TA": (Entity("Tarrafal", "CV-TA", "MUNICIPALITY", "pt", "CV-S"),),
        "CV-TS": (Entity("Tarrafal de São Nicolau", "CV-TS", "MUNICIPALITY", "pt", "CV-B"),),
    }
