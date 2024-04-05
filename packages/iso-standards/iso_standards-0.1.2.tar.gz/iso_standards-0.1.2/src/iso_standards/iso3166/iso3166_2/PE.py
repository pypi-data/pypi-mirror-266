"""ISO 3166-2 PE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PE-AMA": (
            Entity("Amarumayu", "PE-AMA", "REGION", "qu", ""),
            Entity("Amasunu", "PE-AMA", "REGION", "ay", ""),
            Entity("Amazonas", "PE-AMA", "REGION", "es", ""),
        ),
        "PE-ANC": (
            Entity("Ancash", "PE-ANC", "REGION", "es", ""),
            Entity("Ankashu", "PE-ANC", "REGION", "ay", ""),
            Entity("Anqash", "PE-ANC", "REGION", "qu", ""),
        ),
        "PE-APU": (
            Entity("Apurimaq", "PE-APU", "REGION", "ay", ""),
            Entity("Apurimaq", "PE-APU", "REGION", "qu", ""),
            Entity("Apurímac", "PE-APU", "REGION", "es", ""),
        ),
        "PE-ARE": (
            Entity("Arequipa", "PE-ARE", "REGION", "es", ""),
            Entity("Arikipa", "PE-ARE", "REGION", "ay", ""),
            Entity("Ariqipa", "PE-ARE", "REGION", "qu", ""),
        ),
        "PE-AYA": (
            Entity("Ayacucho", "PE-AYA", "REGION", "es", ""),
            Entity("Ayakuchu", "PE-AYA", "REGION", "qu", ""),
            Entity("Ayaquchu", "PE-AYA", "REGION", "ay", ""),
        ),
        "PE-CAJ": (
            Entity("Cajamarca", "PE-CAJ", "REGION", "es", ""),
            Entity("Kashamarka", "PE-CAJ", "REGION", "qu", ""),
            Entity("Qajamarka", "PE-CAJ", "REGION", "ay", ""),
        ),
        "PE-CAL": (
            Entity("El Callao", "PE-CAL", "REGION", "es", ""),
            Entity("Kallao", "PE-CAL", "REGION", "ay", ""),
            Entity("Qallaw", "PE-CAL", "REGION", "qu", ""),
        ),
        "PE-CUS": (
            Entity("Cusco", "PE-CUS", "REGION", "es", ""),
            Entity("Kusku", "PE-CUS", "REGION", "ay", ""),
            Entity("Qusqu", "PE-CUS", "REGION", "qu", ""),
        ),
        "PE-HUC": (
            Entity("Huánuco", "PE-HUC", "REGION", "es", ""),
            Entity("Wanuku", "PE-HUC", "REGION", "ay", ""),
            Entity("Wanuku", "PE-HUC", "REGION", "qu", ""),
        ),
        "PE-HUV": (
            Entity("Huancavelica", "PE-HUV", "REGION", "es", ""),
            Entity("Wankawelika", "PE-HUV", "REGION", "ay", ""),
            Entity("Wankawillka", "PE-HUV", "REGION", "qu", ""),
        ),
        "PE-ICA": (
            Entity("Ica", "PE-ICA", "REGION", "es", ""),
            Entity("Ika", "PE-ICA", "REGION", "ay", ""),
            Entity("Ika", "PE-ICA", "REGION", "qu", ""),
        ),
        "PE-JUN": (
            Entity("Hunin", "PE-JUN", "REGION", "qu", ""),
            Entity("Junin", "PE-JUN", "REGION", "ay", ""),
            Entity("Junín", "PE-JUN", "REGION", "es", ""),
        ),
        "PE-LAL": (
            Entity("La Libertad", "PE-LAL", "REGION", "ay", ""),
            Entity("La Libertad", "PE-LAL", "REGION", "es", ""),
            Entity("Qispi kay", "PE-LAL", "REGION", "qu", ""),
        ),
        "PE-LAM": (
            Entity("Lambayeque", "PE-LAM", "REGION", "ay", ""),
            Entity("Lambayeque", "PE-LAM", "REGION", "es", ""),
            Entity("Lampalliqi", "PE-LAM", "REGION", "qu", ""),
        ),
        "PE-LIM": (
            Entity("Lima", "PE-LIM", "REGION", "ay", ""),
            Entity("Lima", "PE-LIM", "REGION", "qu", ""),
            Entity("Lima", "PE-LIM", "REGION", "es", ""),
        ),
        "PE-LMA": (
            Entity("Lima hatun llaqta", "PE-LMA", "MUNICIPALITY", "ay", ""),
            Entity("Lima llaqta suyu", "PE-LMA", "MUNICIPALITY", "qu", ""),
            Entity("Municipalidad Metropolitana de Lima", "PE-LMA", "MUNICIPALITY", "es", ""),
        ),
        "PE-LOR": (
            Entity("Loreto", "PE-LOR", "REGION", "es", ""),
            Entity("Luritu", "PE-LOR", "REGION", "ay", ""),
            Entity("Luritu", "PE-LOR", "REGION", "qu", ""),
        ),
        "PE-MDD": (
            Entity("Madre de Dios", "PE-MDD", "REGION", "ay", ""),
            Entity("Madre de Dios", "PE-MDD", "REGION", "es", ""),
            Entity("Mayutata", "PE-MDD", "REGION", "qu", ""),
        ),
        "PE-MOQ": (
            Entity("Moquegua", "PE-MOQ", "REGION", "es", ""),
            Entity("Moqwegwa", "PE-MOQ", "REGION", "ay", ""),
            Entity("Muqiwa", "PE-MOQ", "REGION", "qu", ""),
        ),
        "PE-PAS": (
            Entity("Pasco", "PE-PAS", "REGION", "es", ""),
            Entity("Pasqu", "PE-PAS", "REGION", "ay", ""),
            Entity("Pasqu", "PE-PAS", "REGION", "qu", ""),
        ),
        "PE-PIU": (
            Entity("Piura", "PE-PIU", "REGION", "ay", ""),
            Entity("Piura", "PE-PIU", "REGION", "es", ""),
            Entity("Piwra", "PE-PIU", "REGION", "qu", ""),
        ),
        "PE-PUN": (
            Entity("Puno", "PE-PUN", "REGION", "ay", ""),
            Entity("Puno", "PE-PUN", "REGION", "es", ""),
            Entity("Punu", "PE-PUN", "REGION", "qu", ""),
        ),
        "PE-SAM": (
            Entity("San Martin", "PE-SAM", "REGION", "qu", ""),
            Entity("San Martín", "PE-SAM", "REGION", "ay", ""),
            Entity("San Martín", "PE-SAM", "REGION", "es", ""),
        ),
        "PE-TAC": (
            Entity("Tacna", "PE-TAC", "REGION", "es", ""),
            Entity("Takna", "PE-TAC", "REGION", "ay", ""),
            Entity("Taqna", "PE-TAC", "REGION", "qu", ""),
        ),
        "PE-TUM": (
            Entity("Tumbes", "PE-TUM", "REGION", "ay", ""),
            Entity("Tumbes", "PE-TUM", "REGION", "es", ""),
            Entity("Tumpis", "PE-TUM", "REGION", "qu", ""),
        ),
        "PE-UCA": (
            Entity("Ucayali", "PE-UCA", "REGION", "es", ""),
            Entity("Ukayali", "PE-UCA", "REGION", "ay", ""),
            Entity("Ukayali", "PE-UCA", "REGION", "qu", ""),
        ),
    }
