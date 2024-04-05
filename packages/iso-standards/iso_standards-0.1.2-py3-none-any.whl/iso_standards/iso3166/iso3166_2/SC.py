"""ISO 3166-2 SC standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SC
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SC-01": (
            Entity("Ans o Pen", "SC-01", "DISTRICT", "", ""),
            Entity("Anse aux Pins", "SC-01", "DISTRICT", "en", ""),
            Entity("Anse aux Pins", "SC-01", "DISTRICT", "fr", ""),
        ),
        "SC-02": (
            Entity("Ans Bwalo", "SC-02", "DISTRICT", "", ""),
            Entity("Anse Boileau", "SC-02", "DISTRICT", "en", ""),
            Entity("Anse Boileau", "SC-02", "DISTRICT", "fr", ""),
        ),
        "SC-03": (
            Entity("Ans Etwal", "SC-03", "DISTRICT", "", ""),
            Entity("Anse Etoile", "SC-03", "DISTRICT", "en", ""),
            Entity("Anse Étoile", "SC-03", "DISTRICT", "fr", ""),
        ),
        "SC-04": (
            Entity("Au Cap", "SC-04", "DISTRICT", "en", ""),
            Entity("Au Cap", "SC-04", "DISTRICT", "fr", ""),
            Entity("O Kap", "SC-04", "DISTRICT", "", ""),
        ),
        "SC-05": (
            Entity("Ans Royal", "SC-05", "DISTRICT", "", ""),
            Entity("Anse Royale", "SC-05", "DISTRICT", "en", ""),
            Entity("Anse Royale", "SC-05", "DISTRICT", "fr", ""),
        ),
        "SC-06": (
            Entity("Baie Lazare", "SC-06", "DISTRICT", "en", ""),
            Entity("Baie Lazare", "SC-06", "DISTRICT", "fr", ""),
            Entity("Be Lazar", "SC-06", "DISTRICT", "", ""),
        ),
        "SC-07": (
            Entity("Baie Sainte Anne", "SC-07", "DISTRICT", "en", ""),
            Entity("Baie Sainte-Anne", "SC-07", "DISTRICT", "fr", ""),
            Entity("Be Sent Ann", "SC-07", "DISTRICT", "", ""),
        ),
        "SC-08": (
            Entity("Beau Vallon", "SC-08", "DISTRICT", "en", ""),
            Entity("Beau Vallon", "SC-08", "DISTRICT", "fr", ""),
            Entity("Bovalon", "SC-08", "DISTRICT", "", ""),
        ),
        "SC-09": (
            Entity("Bel Air", "SC-09", "DISTRICT", "en", ""),
            Entity("Bel Air", "SC-09", "DISTRICT", "fr", ""),
            Entity("Beler", "SC-09", "DISTRICT", "", ""),
        ),
        "SC-10": (
            Entity("Bel Ombre", "SC-10", "DISTRICT", "en", ""),
            Entity("Bel Ombre", "SC-10", "DISTRICT", "fr", ""),
            Entity("Belonm", "SC-10", "DISTRICT", "", ""),
        ),
        "SC-11": (
            Entity("Cascade", "SC-11", "DISTRICT", "en", ""),
            Entity("Cascade", "SC-11", "DISTRICT", "fr", ""),
            Entity("Kaskad", "SC-11", "DISTRICT", "", ""),
        ),
        "SC-12": (
            Entity("Glacis", "SC-12", "DISTRICT", "en", ""),
            Entity("Glacis", "SC-12", "DISTRICT", "fr", ""),
            Entity("Glasi", "SC-12", "DISTRICT", "", ""),
        ),
        "SC-13": (
            Entity("Grand Ans Mae", "SC-13", "DISTRICT", "", ""),
            Entity("Grand Anse Mahe", "SC-13", "DISTRICT", "en", ""),
            Entity("Grand'Anse Mahé", "SC-13", "DISTRICT", "fr", ""),
        ),
        "SC-14": (
            Entity("Grand Ans Pralen", "SC-14", "DISTRICT", "", ""),
            Entity("Grand Anse Praslin", "SC-14", "DISTRICT", "en", ""),
            Entity("Grand'Anse Praslin", "SC-14", "DISTRICT", "fr", ""),
        ),
        "SC-15": (
            Entity("La Digue", "SC-15", "DISTRICT", "en", ""),
            Entity("La Digue", "SC-15", "DISTRICT", "fr", ""),
            Entity("Ladig", "SC-15", "DISTRICT", "", ""),
        ),
        "SC-16": (
            Entity("English River", "SC-16", "DISTRICT", "en", ""),
            Entity("La Rivière Anglaise", "SC-16", "DISTRICT", "fr", ""),
            Entity("Larivyer Anglez", "SC-16", "DISTRICT", "", ""),
        ),
        "SC-17": (
            Entity("Mon Bikston", "SC-17", "DISTRICT", "", ""),
            Entity("Mont Buxton", "SC-17", "DISTRICT", "en", ""),
            Entity("Mont Buxton", "SC-17", "DISTRICT", "fr", ""),
        ),
        "SC-18": (
            Entity("Mon Fleri", "SC-18", "DISTRICT", "", ""),
            Entity("Mont Fleuri", "SC-18", "DISTRICT", "en", ""),
            Entity("Mont Fleuri", "SC-18", "DISTRICT", "fr", ""),
        ),
        "SC-19": (
            Entity("Plaisance", "SC-19", "DISTRICT", "en", ""),
            Entity("Plaisance", "SC-19", "DISTRICT", "fr", ""),
            Entity("Plezans", "SC-19", "DISTRICT", "", ""),
        ),
        "SC-20": (
            Entity("Pointe La Rue", "SC-20", "DISTRICT", "fr", ""),
            Entity("Pointe Larue", "SC-20", "DISTRICT", "en", ""),
            Entity("Pwent Lari", "SC-20", "DISTRICT", "", ""),
        ),
        "SC-21": (
            Entity("Porglo", "SC-21", "DISTRICT", "", ""),
            Entity("Port Glaud", "SC-21", "DISTRICT", "en", ""),
            Entity("Port Glaud", "SC-21", "DISTRICT", "fr", ""),
        ),
        "SC-22": (
            Entity("Saint Louis", "SC-22", "DISTRICT", "en", ""),
            Entity("Saint-Louis", "SC-22", "DISTRICT", "fr", ""),
            Entity("Sen Lwi", "SC-22", "DISTRICT", "", ""),
        ),
        "SC-23": (
            Entity("Takamaka", "SC-23", "DISTRICT", "", ""),
            Entity("Takamaka", "SC-23", "DISTRICT", "en", ""),
            Entity("Takamaka", "SC-23", "DISTRICT", "fr", ""),
        ),
        "SC-24": (
            Entity("Lemamel", "SC-24", "DISTRICT", "", ""),
            Entity("Les Mamelles", "SC-24", "DISTRICT", "en", ""),
            Entity("Les Mamelles", "SC-24", "DISTRICT", "fr", ""),
        ),
        "SC-25": (
            Entity("Roche Caiman", "SC-25", "DISTRICT", "en", ""),
            Entity("Roche Caïman", "SC-25", "DISTRICT", "fr", ""),
            Entity("Ros Kaiman", "SC-25", "DISTRICT", "", ""),
        ),
        "SC-26": (
            Entity("Ile Perseverance I", "SC-26", "DISTRICT", "en", ""),
            Entity("Île Persévérance I", "SC-26", "DISTRICT", "fr", ""),
        ),
        "SC-27": (
            Entity("Ile Perseverance II", "SC-27", "DISTRICT", "en", ""),
            Entity("Île Persévérance II", "SC-27", "DISTRICT", "fr", ""),
        ),
    }
