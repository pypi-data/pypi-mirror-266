"""ISO 3166-2 BR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BR-AC": (Entity("Acre", "BR-AC", "STATE", "pt", ""),),
        "BR-AL": (Entity("Alagoas", "BR-AL", "STATE", "pt", ""),),
        "BR-AM": (Entity("Amazonas", "BR-AM", "STATE", "pt", ""),),
        "BR-AP": (Entity("Amapá", "BR-AP", "STATE", "pt", ""),),
        "BR-BA": (Entity("Bahia", "BR-BA", "STATE", "pt", ""),),
        "BR-CE": (Entity("Ceará", "BR-CE", "STATE", "pt", ""),),
        "BR-DF": (Entity("Distrito Federal", "BR-DF", "FEDERAL DISTRICT", "pt", ""),),
        "BR-ES": (Entity("Espírito Santo", "BR-ES", "STATE", "pt", ""),),
        "BR-GO": (Entity("Goiás", "BR-GO", "STATE", "pt", ""),),
        "BR-MA": (Entity("Maranhão", "BR-MA", "STATE", "pt", ""),),
        "BR-MG": (Entity("Minas Gerais", "BR-MG", "STATE", "pt", ""),),
        "BR-MS": (Entity("Mato Grosso do Sul", "BR-MS", "STATE", "pt", ""),),
        "BR-MT": (Entity("Mato Grosso", "BR-MT", "STATE", "pt", ""),),
        "BR-PA": (Entity("Pará", "BR-PA", "STATE", "pt", ""),),
        "BR-PB": (Entity("Paraíba", "BR-PB", "STATE", "pt", ""),),
        "BR-PE": (Entity("Pernambuco", "BR-PE", "STATE", "pt", ""),),
        "BR-PI": (Entity("Piauí", "BR-PI", "STATE", "pt", ""),),
        "BR-PR": (Entity("Paraná", "BR-PR", "STATE", "pt", ""),),
        "BR-RJ": (Entity("Rio de Janeiro", "BR-RJ", "STATE", "pt", ""),),
        "BR-RN": (Entity("Rio Grande do Norte", "BR-RN", "STATE", "pt", ""),),
        "BR-RO": (Entity("Rondônia", "BR-RO", "STATE", "pt", ""),),
        "BR-RR": (Entity("Roraima", "BR-RR", "STATE", "pt", ""),),
        "BR-RS": (Entity("Rio Grande do Sul", "BR-RS", "STATE", "pt", ""),),
        "BR-SC": (Entity("Santa Catarina", "BR-SC", "STATE", "pt", ""),),
        "BR-SE": (Entity("Sergipe", "BR-SE", "STATE", "pt", ""),),
        "BR-SP": (Entity("São Paulo", "BR-SP", "STATE", "pt", ""),),
        "BR-TO": (Entity("Tocantins", "BR-TO", "STATE", "pt", ""),),
    }
