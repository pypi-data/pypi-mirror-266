"""ISO 3166-2 MC standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MC
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MC-CL": (Entity("La Colle", "MC-CL", "QUARTER", "fr", ""),),
        "MC-CO": (Entity("La Condamine", "MC-CO", "QUARTER", "fr", ""),),
        "MC-FO": (Entity("Fontvieille", "MC-FO", "QUARTER", "fr", ""),),
        "MC-GA": (Entity("La Gare", "MC-GA", "QUARTER", "fr", ""),),
        "MC-JE": (Entity("Jardin Exotique", "MC-JE", "QUARTER", "fr", ""),),
        "MC-LA": (Entity("Larvotto", "MC-LA", "QUARTER", "fr", ""),),
        "MC-MA": (Entity("Malbousquet", "MC-MA", "QUARTER", "fr", ""),),
        "MC-MC": (Entity("Monte-Carlo", "MC-MC", "QUARTER", "fr", ""),),
        "MC-MG": (Entity("Moneghetti", "MC-MG", "QUARTER", "fr", ""),),
        "MC-MO": (Entity("Monaco-Ville", "MC-MO", "QUARTER", "fr", ""),),
        "MC-MU": (Entity("Moulins", "MC-MU", "QUARTER", "fr", ""),),
        "MC-PH": (Entity("Port-Hercule", "MC-PH", "QUARTER", "fr", ""),),
        "MC-SD": (Entity("Sainte-Dévote", "MC-SD", "QUARTER", "fr", ""),),
        "MC-SO": (Entity("La Source", "MC-SO", "QUARTER", "fr", ""),),
        "MC-SP": (Entity("Spélugues", "MC-SP", "QUARTER", "fr", ""),),
        "MC-SR": (Entity("Saint-Roman", "MC-SR", "QUARTER", "fr", ""),),
        "MC-VR": (Entity("Vallon de la Rousse", "MC-VR", "QUARTER", "fr", ""),),
    }
