"""ISO 3166-2 AF standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:AF
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "AF-BAL": (
            Entity("Balkh", "AF-BAL", "PROVINCE", "fa", ""),
            Entity("Balkh", "AF-BAL", "PROVINCE", "ps", ""),
        ),
        "AF-BAM": (
            Entity("Bāmyān", "AF-BAM", "PROVINCE", "fa", ""),
            Entity("Bāmyān", "AF-BAM", "PROVINCE", "ps", ""),
        ),
        "AF-BDG": (
            Entity("Bādghīs", "AF-BDG", "PROVINCE", "fa", ""),
            Entity("Bādghīs", "AF-BDG", "PROVINCE", "ps", ""),
        ),
        "AF-BDS": (
            Entity("Badakhshān", "AF-BDS", "PROVINCE", "fa", ""),
            Entity("Badakhshān", "AF-BDS", "PROVINCE", "ps", ""),
        ),
        "AF-BGL": (
            Entity("Baghlān", "AF-BGL", "PROVINCE", "fa", ""),
            Entity("Baghlān", "AF-BGL", "PROVINCE", "ps", ""),
        ),
        "AF-DAY": (
            Entity("Dāykundī", "AF-DAY", "PROVINCE", "fa", ""),
            Entity("Dāykundī", "AF-DAY", "PROVINCE", "ps", ""),
        ),
        "AF-FRA": (
            Entity("Farāh", "AF-FRA", "PROVINCE", "fa", ""),
            Entity("Farāh", "AF-FRA", "PROVINCE", "ps", ""),
        ),
        "AF-FYB": (
            Entity("Fāryāb", "AF-FYB", "PROVINCE", "fa", ""),
            Entity("Fāryāb", "AF-FYB", "PROVINCE", "ps", ""),
        ),
        "AF-GHA": (
            Entity("Ghaznī", "AF-GHA", "PROVINCE", "fa", ""),
            Entity("Ghaznī", "AF-GHA", "PROVINCE", "ps", ""),
        ),
        "AF-GHO": (
            Entity("Ghōr", "AF-GHO", "PROVINCE", "fa", ""),
            Entity("Ghōr", "AF-GHO", "PROVINCE", "ps", ""),
        ),
        "AF-HEL": (
            Entity("Helmand", "AF-HEL", "PROVINCE", "fa", ""),
            Entity("Helmand", "AF-HEL", "PROVINCE", "ps", ""),
        ),
        "AF-HER": (
            Entity("Herāt", "AF-HER", "PROVINCE", "fa", ""),
            Entity("Herāt", "AF-HER", "PROVINCE", "ps", ""),
        ),
        "AF-JOW": (
            Entity("Jowzjān", "AF-JOW", "PROVINCE", "fa", ""),
            Entity("Jowzjān", "AF-JOW", "PROVINCE", "ps", ""),
        ),
        "AF-KAB": (
            Entity("Kābul", "AF-KAB", "PROVINCE", "fa", ""),
            Entity("Kābul", "AF-KAB", "PROVINCE", "ps", ""),
        ),
        "AF-KAN": (
            Entity("Kandahār", "AF-KAN", "PROVINCE", "fa", ""),
            Entity("Kandahār", "AF-KAN", "PROVINCE", "ps", ""),
        ),
        "AF-KAP": (
            Entity("Kāpīsā", "AF-KAP", "PROVINCE", "fa", ""),
            Entity("Kāpīsā", "AF-KAP", "PROVINCE", "ps", ""),
        ),
        "AF-KDZ": (
            Entity("Kunduz", "AF-KDZ", "PROVINCE", "fa", ""),
            Entity("Kunduz", "AF-KDZ", "PROVINCE", "ps", ""),
        ),
        "AF-KHO": (
            Entity("Khōst", "AF-KHO", "PROVINCE", "fa", ""),
            Entity("Khōst", "AF-KHO", "PROVINCE", "ps", ""),
        ),
        "AF-KNR": (
            Entity("Kunaṟ", "AF-KNR", "PROVINCE", "fa", ""),
            Entity("Kunaṟ", "AF-KNR", "PROVINCE", "ps", ""),
        ),
        "AF-LAG": (
            Entity("Laghmān", "AF-LAG", "PROVINCE", "fa", ""),
            Entity("Laghmān", "AF-LAG", "PROVINCE", "ps", ""),
        ),
        "AF-LOG": (
            Entity("Lōgar", "AF-LOG", "PROVINCE", "fa", ""),
            Entity("Lōgar", "AF-LOG", "PROVINCE", "ps", ""),
        ),
        "AF-NAN": (
            Entity("Nangarhār", "AF-NAN", "PROVINCE", "fa", ""),
            Entity("Nangarhār", "AF-NAN", "PROVINCE", "ps", ""),
        ),
        "AF-NIM": (
            Entity("Nīmrōz", "AF-NIM", "PROVINCE", "fa", ""),
            Entity("Nīmrōz", "AF-NIM", "PROVINCE", "ps", ""),
        ),
        "AF-NUR": (
            Entity("Nūristān", "AF-NUR", "PROVINCE", "fa", ""),
            Entity("Nūristān", "AF-NUR", "PROVINCE", "ps", ""),
        ),
        "AF-PAN": (
            Entity("Panjshayr", "AF-PAN", "PROVINCE", "fa", ""),
            Entity("Panjshayr", "AF-PAN", "PROVINCE", "ps", ""),
        ),
        "AF-PAR": (
            Entity("Parwān", "AF-PAR", "PROVINCE", "fa", ""),
            Entity("Parwān", "AF-PAR", "PROVINCE", "ps", ""),
        ),
        "AF-PIA": (
            Entity("Paktiyā", "AF-PIA", "PROVINCE", "fa", ""),
            Entity("Paktiyā", "AF-PIA", "PROVINCE", "ps", ""),
        ),
        "AF-PKA": (
            Entity("Paktīkā", "AF-PKA", "PROVINCE", "fa", ""),
            Entity("Paktīkā", "AF-PKA", "PROVINCE", "ps", ""),
        ),
        "AF-SAM": (
            Entity("Samangān", "AF-SAM", "PROVINCE", "fa", ""),
            Entity("Samangān", "AF-SAM", "PROVINCE", "ps", ""),
        ),
        "AF-SAR": (
            Entity("Sar-e Pul", "AF-SAR", "PROVINCE", "fa", ""),
            Entity("Sar-e Pul", "AF-SAR", "PROVINCE", "ps", ""),
        ),
        "AF-TAK": (
            Entity("Takhār", "AF-TAK", "PROVINCE", "fa", ""),
            Entity("Takhār", "AF-TAK", "PROVINCE", "ps", ""),
        ),
        "AF-URU": (
            Entity("Uruzgān", "AF-URU", "PROVINCE", "fa", ""),
            Entity("Uruzgān", "AF-URU", "PROVINCE", "ps", ""),
        ),
        "AF-WAR": (
            Entity("Wardak", "AF-WAR", "PROVINCE", "fa", ""),
            Entity("Wardak", "AF-WAR", "PROVINCE", "ps", ""),
        ),
        "AF-ZAB": (
            Entity("Zābul", "AF-ZAB", "PROVINCE", "fa", ""),
            Entity("Zābul", "AF-ZAB", "PROVINCE", "ps", ""),
        ),
    }
