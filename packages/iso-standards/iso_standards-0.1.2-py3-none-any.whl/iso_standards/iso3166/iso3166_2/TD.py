"""ISO 3166-2 TD standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TD
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TD-BA": (
            Entity("Al Baţḩā’", "TD-BA", "PROVINCE", "ar", ""),
            Entity("Batha", "TD-BA", "PROVINCE", "fr", ""),
        ),
        "TD-BG": (
            Entity("Bahr el Ghazal", "TD-BG", "PROVINCE", "fr", ""),
            Entity("Baḩr al Ghazāl", "TD-BG", "PROVINCE", "ar", ""),
        ),
        "TD-BO": (
            Entity("Borkou", "TD-BO", "PROVINCE", "fr", ""),
            Entity("Būrkū", "TD-BO", "PROVINCE", "ar", ""),
        ),
        "TD-CB": (
            Entity("Chari-Baguirmi", "TD-CB", "PROVINCE", "fr", ""),
            Entity("Shārī Bāqirmī", "TD-CB", "PROVINCE", "ar", ""),
        ),
        "TD-EE": (
            Entity("Ennedi-Est", "TD-EE", "PROVINCE", "fr", ""),
            Entity("Inīdī ash Sharqī", "TD-EE", "PROVINCE", "ar", ""),
        ),
        "TD-EO": (
            Entity("Ennedi-Ouest", "TD-EO", "PROVINCE", "fr", ""),
            Entity("Inīdī al Gharbī", "TD-EO", "PROVINCE", "ar", ""),
        ),
        "TD-GR": (
            Entity("Guéra", "TD-GR", "PROVINCE", "fr", ""),
            Entity("Qīrā", "TD-GR", "PROVINCE", "ar", ""),
        ),
        "TD-HL": (
            Entity("Hadjer Lamis", "TD-HL", "PROVINCE", "fr", ""),
            Entity("Ḩajjar Lamīs", "TD-HL", "PROVINCE", "ar", ""),
        ),
        "TD-KA": (
            Entity("Kanem", "TD-KA", "PROVINCE", "fr", ""),
            Entity("Kānim", "TD-KA", "PROVINCE", "ar", ""),
        ),
        "TD-LC": (
            Entity("Al Buḩayrah", "TD-LC", "PROVINCE", "ar", ""),
            Entity("Lac", "TD-LC", "PROVINCE", "fr", ""),
        ),
        "TD-LO": (
            Entity("Logone-Occidental", "TD-LO", "PROVINCE", "fr", ""),
            Entity("Lūghūn al Gharbī", "TD-LO", "PROVINCE", "ar", ""),
        ),
        "TD-LR": (
            Entity("Logone-Oriental", "TD-LR", "PROVINCE", "fr", ""),
            Entity("Lūghūn ash Sharqī", "TD-LR", "PROVINCE", "ar", ""),
        ),
        "TD-MA": (
            Entity("Mandoul", "TD-MA", "PROVINCE", "fr", ""),
            Entity("Māndūl", "TD-MA", "PROVINCE", "ar", ""),
        ),
        "TD-MC": (
            Entity("Moyen-Chari", "TD-MC", "PROVINCE", "fr", ""),
            Entity("Shārī al Awsaţ", "TD-MC", "PROVINCE", "ar", ""),
        ),
        "TD-ME": (
            Entity("Mayo-Kebbi-Est", "TD-ME", "PROVINCE", "fr", ""),
            Entity("Māyū Kībbī ash Sharqī", "TD-ME", "PROVINCE", "ar", ""),
        ),
        "TD-MO": (
            Entity("Mayo-Kebbi-Ouest", "TD-MO", "PROVINCE", "fr", ""),
            Entity("Māyū Kībbī al Gharbī", "TD-MO", "PROVINCE", "ar", ""),
        ),
        "TD-ND": (
            Entity("Madīnat Injamīnā", "TD-ND", "PROVINCE", "ar", ""),
            Entity("Ville de Ndjamena", "TD-ND", "PROVINCE", "fr", ""),
        ),
        "TD-OD": (
            Entity("Ouaddaï", "TD-OD", "PROVINCE", "fr", ""),
            Entity("Waddāy", "TD-OD", "PROVINCE", "ar", ""),
        ),
        "TD-SA": (
            Entity("Salamat", "TD-SA", "PROVINCE", "fr", ""),
            Entity("Salāmāt", "TD-SA", "PROVINCE", "ar", ""),
        ),
        "TD-SI": (
            Entity("Sila", "TD-SI", "PROVINCE", "fr", ""),
            Entity("Sīlā", "TD-SI", "PROVINCE", "ar", ""),
        ),
        "TD-TA": (
            Entity("Tandjilé", "TD-TA", "PROVINCE", "fr", ""),
            Entity("Tānjīlī", "TD-TA", "PROVINCE", "ar", ""),
        ),
        "TD-TI": (
            Entity("Tibastī", "TD-TI", "PROVINCE", "ar", ""),
            Entity("Tibesti", "TD-TI", "PROVINCE", "fr", ""),
        ),
        "TD-WF": (
            Entity("Wadi Fira", "TD-WF", "PROVINCE", "fr", ""),
            Entity("Wādī Fīrā’", "TD-WF", "PROVINCE", "ar", ""),
        ),
    }
