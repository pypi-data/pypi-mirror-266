"""ISO 3166-2 BF standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BF
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BF-01": (Entity("Boucle du Mouhoun", "BF-01", "REGION", "fr", ""),),
        "BF-02": (Entity("Cascades", "BF-02", "REGION", "fr", ""),),
        "BF-03": (Entity("Centre", "BF-03", "REGION", "fr", ""),),
        "BF-04": (Entity("Centre-Est", "BF-04", "REGION", "fr", ""),),
        "BF-05": (Entity("Centre-Nord", "BF-05", "REGION", "fr", ""),),
        "BF-06": (Entity("Centre-Ouest", "BF-06", "REGION", "fr", ""),),
        "BF-07": (Entity("Centre-Sud", "BF-07", "REGION", "fr", ""),),
        "BF-08": (Entity("Est", "BF-08", "REGION", "fr", ""),),
        "BF-09": (Entity("Hauts-Bassins", "BF-09", "REGION", "fr", ""),),
        "BF-10": (Entity("Nord", "BF-10", "REGION", "fr", ""),),
        "BF-11": (Entity("Plateau-Central", "BF-11", "REGION", "fr", ""),),
        "BF-12": (Entity("Sahel", "BF-12", "REGION", "fr", ""),),
        "BF-13": (Entity("Sud-Ouest", "BF-13", "REGION", "fr", ""),),
        "BF-BAL": (Entity("Balé", "BF-BAL", "PROVINCE", "fr", "BF-01"),),
        "BF-BAM": (Entity("Bam", "BF-BAM", "PROVINCE", "fr", "BF-05"),),
        "BF-BAN": (Entity("Banwa", "BF-BAN", "PROVINCE", "fr", "BF-01"),),
        "BF-BAZ": (Entity("Bazèga", "BF-BAZ", "PROVINCE", "fr", "BF-07"),),
        "BF-BGR": (Entity("Bougouriba", "BF-BGR", "PROVINCE", "fr", "BF-13"),),
        "BF-BLG": (Entity("Boulgou", "BF-BLG", "PROVINCE", "fr", "BF-04"),),
        "BF-BLK": (Entity("Boulkiemdé", "BF-BLK", "PROVINCE", "fr", "BF-06"),),
        "BF-COM": (Entity("Comoé", "BF-COM", "PROVINCE", "fr", "BF-02"),),
        "BF-GAN": (Entity("Ganzourgou", "BF-GAN", "PROVINCE", "fr", "BF-11"),),
        "BF-GNA": (Entity("Gnagna", "BF-GNA", "PROVINCE", "fr", "BF-08"),),
        "BF-GOU": (Entity("Gourma", "BF-GOU", "PROVINCE", "fr", "BF-08"),),
        "BF-HOU": (Entity("Houet", "BF-HOU", "PROVINCE", "fr", "BF-09"),),
        "BF-IOB": (Entity("Ioba", "BF-IOB", "PROVINCE", "fr", "BF-13"),),
        "BF-KAD": (Entity("Kadiogo", "BF-KAD", "PROVINCE", "fr", "BF-03"),),
        "BF-KEN": (Entity("Kénédougou", "BF-KEN", "PROVINCE", "fr", "BF-09"),),
        "BF-KMD": (Entity("Komondjari", "BF-KMD", "PROVINCE", "fr", "BF-08"),),
        "BF-KMP": (Entity("Kompienga", "BF-KMP", "PROVINCE", "fr", "BF-08"),),
        "BF-KOP": (Entity("Koulpélogo", "BF-KOP", "PROVINCE", "fr", "BF-04"),),
        "BF-KOS": (Entity("Kossi", "BF-KOS", "PROVINCE", "fr", "BF-01"),),
        "BF-KOT": (Entity("Kouritenga", "BF-KOT", "PROVINCE", "fr", "BF-04"),),
        "BF-KOW": (Entity("Kourwéogo", "BF-KOW", "PROVINCE", "fr", "BF-11"),),
        "BF-LER": (Entity("Léraba", "BF-LER", "PROVINCE", "fr", "BF-02"),),
        "BF-LOR": (Entity("Loroum", "BF-LOR", "PROVINCE", "fr", "BF-10"),),
        "BF-MOU": (Entity("Mouhoun", "BF-MOU", "PROVINCE", "fr", "BF-01"),),
        "BF-NAM": (Entity("Namentenga", "BF-NAM", "PROVINCE", "fr", "BF-05"),),
        "BF-NAO": (Entity("Nahouri", "BF-NAO", "PROVINCE", "fr", "BF-07"),),
        "BF-NAY": (Entity("Nayala", "BF-NAY", "PROVINCE", "fr", "BF-01"),),
        "BF-NOU": (Entity("Noumbiel", "BF-NOU", "PROVINCE", "fr", "BF-13"),),
        "BF-OUB": (Entity("Oubritenga", "BF-OUB", "PROVINCE", "fr", "BF-11"),),
        "BF-OUD": (Entity("Oudalan", "BF-OUD", "PROVINCE", "fr", "BF-12"),),
        "BF-PAS": (Entity("Passoré", "BF-PAS", "PROVINCE", "fr", "BF-10"),),
        "BF-PON": (Entity("Poni", "BF-PON", "PROVINCE", "fr", "BF-13"),),
        "BF-SEN": (Entity("Séno", "BF-SEN", "PROVINCE", "fr", "BF-12"),),
        "BF-SIS": (Entity("Sissili", "BF-SIS", "PROVINCE", "fr", "BF-06"),),
        "BF-SMT": (Entity("Sanmatenga", "BF-SMT", "PROVINCE", "fr", "BF-05"),),
        "BF-SNG": (Entity("Sanguié", "BF-SNG", "PROVINCE", "fr", "BF-06"),),
        "BF-SOM": (Entity("Soum", "BF-SOM", "PROVINCE", "fr", "BF-12"),),
        "BF-SOR": (Entity("Sourou", "BF-SOR", "PROVINCE", "fr", "BF-01"),),
        "BF-TAP": (Entity("Tapoa", "BF-TAP", "PROVINCE", "fr", "BF-08"),),
        "BF-TUI": (Entity("Tuy", "BF-TUI", "PROVINCE", "fr", "BF-09"),),
        "BF-YAG": (Entity("Yagha", "BF-YAG", "PROVINCE", "fr", "BF-12"),),
        "BF-YAT": (Entity("Yatenga", "BF-YAT", "PROVINCE", "fr", "BF-10"),),
        "BF-ZIR": (Entity("Ziro", "BF-ZIR", "PROVINCE", "fr", "BF-06"),),
        "BF-ZON": (Entity("Zondoma", "BF-ZON", "PROVINCE", "fr", "BF-10"),),
        "BF-ZOU": (Entity("Zoundwéogo", "BF-ZOU", "PROVINCE", "fr", "BF-07"),),
    }
