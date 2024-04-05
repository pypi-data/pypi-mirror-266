"""ISO 3166-2 ZA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ZA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ZA-EC": (
            Entity("Eastern Cape", "ZA-EC", "PROVINCE", "en", ""),
            Entity("Kapa Bohlabela", "ZA-EC", "PROVINCE", "", ""),
            Entity("Kapa Botjhabela", "ZA-EC", "PROVINCE", "st", ""),
            Entity("Kapa Botlhaba", "ZA-EC", "PROVINCE", "tn", ""),
            Entity("Kapa Vhubvaḓuvha", "ZA-EC", "PROVINCE", "ve", ""),
            Entity("Kapa-Vuxa", "ZA-EC", "PROVINCE", "ts", ""),
            Entity("Mpuma-Koloni", "ZA-EC", "PROVINCE", "xh", ""),
            Entity("Mpumalanga-Kapa", "ZA-EC", "PROVINCE", "zu", ""),
            Entity("Oos-Kaap", "ZA-EC", "PROVINCE", "af", ""),
            Entity("iPumalanga-Kapa", "ZA-EC", "PROVINCE", "nr", ""),
        ),
        "ZA-FS": (
            Entity("Foreisetata", "ZA-FS", "PROVINCE", "tn", ""),
            Entity("Free State", "ZA-FS", "PROVINCE", "en", ""),
            Entity("Free State", "ZA-FS", "PROVINCE", "ts", ""),
            Entity("Freistata", "ZA-FS", "PROVINCE", "", ""),
            Entity("Freistata", "ZA-FS", "PROVINCE", "st", ""),
            Entity("Freyistata", "ZA-FS", "PROVINCE", "xh", ""),
            Entity("Fuleyisitata", "ZA-FS", "PROVINCE", "zu", ""),
            Entity("Fureisitata", "ZA-FS", "PROVINCE", "ve", ""),
            Entity("Vrystaat", "ZA-FS", "PROVINCE", "af", ""),
            Entity("iFreyistata", "ZA-FS", "PROVINCE", "nr", ""),
        ),
        "ZA-GP": (
            Entity("Gauteng", "ZA-GP", "PROVINCE", "af", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "en", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "ss", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "tn", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "ts", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "ve", ""),
            Entity("Gauteng", "ZA-GP", "PROVINCE", "zu", ""),
            Entity("Kgauteng", "ZA-GP", "PROVINCE", "st", ""),
            Entity("Rhawuti", "ZA-GP", "PROVINCE", "xh", ""),
            Entity("iGauteng", "ZA-GP", "PROVINCE", "nr", ""),
        ),
        "ZA-KZN": (
            Entity("GaZulu-Natala", "ZA-KZN", "PROVINCE", "", ""),
            Entity("HaZulu-Natal", "ZA-KZN", "PROVINCE", "ve", ""),
            Entity("Hazolo-Natala", "ZA-KZN", "PROVINCE", "st", ""),
            Entity("KwaZulu-Natal", "ZA-KZN", "PROVINCE", "af", ""),
            Entity("KwaZulu-Natal", "ZA-KZN", "PROVINCE", "tn", ""),
            Entity("KwaZulu-Natala", "ZA-KZN", "PROVINCE", "xh", ""),
            Entity("KwaZulu-Natali", "ZA-KZN", "PROVINCE", "ss", ""),
            Entity("KwaZulu-Natali", "ZA-KZN", "PROVINCE", "zu", ""),
            Entity("Kwazulu-Natal", "ZA-KZN", "PROVINCE", "en", ""),
            Entity("Kwazulu-Natal", "ZA-KZN", "PROVINCE", "ts", ""),
            Entity("iKwaZulu-Natal", "ZA-KZN", "PROVINCE", "nr", ""),
        ),
        "ZA-LP": (
            Entity("Limpopo", "ZA-LP", "PROVINCE", "af", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "en", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "nr", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "st", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "ss", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "tn", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "ts", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "xh", ""),
            Entity("Limpopo", "ZA-LP", "PROVINCE", "zu", ""),
            Entity("Vhembe", "ZA-LP", "PROVINCE", "ve", ""),
        ),
        "ZA-MP": (
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "af", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "en", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "st", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "ss", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "tn", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "ts", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "ve", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "xh", ""),
            Entity("Mpumalanga", "ZA-MP", "PROVINCE", "zu", ""),
            Entity("iMpumalanga", "ZA-MP", "PROVINCE", "nr", ""),
        ),
        "ZA-NC": (
            Entity("Kapa Bokone", "ZA-NC", "PROVINCE", "tn", ""),
            Entity("Kapa Devhula", "ZA-NC", "PROVINCE", "ve", ""),
            Entity("Kapa Leboya", "ZA-NC", "PROVINCE", "", ""),
            Entity("Kapa Leboya", "ZA-NC", "PROVINCE", "st", ""),
            Entity("Kapa-N'walungu", "ZA-NC", "PROVINCE", "ts", ""),
            Entity("Mntla-Koloni", "ZA-NC", "PROVINCE", "xh", ""),
            Entity("Noord-Kaap", "ZA-NC", "PROVINCE", "af", ""),
            Entity("Northern Cape", "ZA-NC", "PROVINCE", "en", ""),
            Entity("Nyakatho-Kapa", "ZA-NC", "PROVINCE", "zu", ""),
            Entity("iTlhagwini-Kapa", "ZA-NC", "PROVINCE", "nr", ""),
        ),
        "ZA-NW": (
            Entity("Bokone Bophirima", "ZA-NW", "PROVINCE", "tn", ""),
            Entity("Lebowa Bodikela", "ZA-NW", "PROVINCE", "", ""),
            Entity("Leboya Bophirima", "ZA-NW", "PROVINCE", "st", ""),
            Entity("Mntla-Ntshona", "ZA-NW", "PROVINCE", "xh", ""),
            Entity("N'walungu-Vupeladyambu", "ZA-NW", "PROVINCE", "ts", ""),
            Entity("Noordwes", "ZA-NW", "PROVINCE", "af", ""),
            Entity("North-West", "ZA-NW", "PROVINCE", "en", ""),
            Entity("Nyakatho-Ntshonalanga", "ZA-NW", "PROVINCE", "zu", ""),
            Entity("iTlhagwini-Tjhingalanga", "ZA-NW", "PROVINCE", "nr", ""),
        ),
        "ZA-WC": (
            Entity("Kapa Bodikela", "ZA-WC", "PROVINCE", "", ""),
            Entity("Kapa Bophirima", "ZA-WC", "PROVINCE", "tn", ""),
            Entity("Kapa Bophirimela", "ZA-WC", "PROVINCE", "st", ""),
            Entity("Kapa Vhukovhela", "ZA-WC", "PROVINCE", "ve", ""),
            Entity("Kapa-Vupeladyambu", "ZA-WC", "PROVINCE", "ts", ""),
            Entity("Ntshona-Koloni", "ZA-WC", "PROVINCE", "xh", ""),
            Entity("Ntshonalanga-Kapa", "ZA-WC", "PROVINCE", "zu", ""),
            Entity("Wes-Kaap", "ZA-WC", "PROVINCE", "af", ""),
            Entity("Western Cape", "ZA-WC", "PROVINCE", "en", ""),
            Entity("iTjhingalanga-Kapa", "ZA-WC", "PROVINCE", "nr", ""),
        ),
    }
