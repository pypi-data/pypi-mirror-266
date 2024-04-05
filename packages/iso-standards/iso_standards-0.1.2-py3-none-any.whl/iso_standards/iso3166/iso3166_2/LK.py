"""ISO 3166-2 LK standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:LK
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "LK-1": (
            Entity("Basnāhira paḷāta", "LK-1", "PROVINCE", "si", ""),
            Entity("Mel mākāṇam", "LK-1", "PROVINCE", "ta", ""),
            Entity("Western Province", "LK-1", "PROVINCE", "en", ""),
        ),
        "LK-11": (
            Entity("Colombo", "LK-11", "DISTRICT", "en", "LK-1"),
            Entity("Kŏl̮umpu", "LK-11", "DISTRICT", "ta", "LK-1"),
            Entity("Kŏḷamba", "LK-11", "DISTRICT", "si", "LK-1"),
        ),
        "LK-12": (
            Entity("Gampaha", "LK-12", "DISTRICT", "en", "LK-1"),
            Entity("Gampaha", "LK-12", "DISTRICT", "si", "LK-1"),
            Entity("Kampahā", "LK-12", "DISTRICT", "ta", "LK-1"),
        ),
        "LK-13": (
            Entity("Kalutara", "LK-13", "DISTRICT", "en", "LK-1"),
            Entity("Kaḷutara", "LK-13", "DISTRICT", "si", "LK-1"),
            Entity("Kaḷuttuṟai", "LK-13", "DISTRICT", "ta", "LK-1"),
        ),
        "LK-2": (
            Entity("Central Province", "LK-2", "PROVINCE", "en", ""),
            Entity("Madhyama paḷāta", "LK-2", "PROVINCE", "si", ""),
            Entity("Mattiya mākāṇam", "LK-2", "PROVINCE", "ta", ""),
        ),
        "LK-21": (
            Entity("Kandy", "LK-21", "DISTRICT", "en", "LK-2"),
            Entity("Kaṇṭi", "LK-21", "DISTRICT", "ta", "LK-2"),
            Entity("Mahanuvara", "LK-21", "DISTRICT", "si", "LK-2"),
        ),
        "LK-22": (
            Entity("Matale", "LK-22", "DISTRICT", "en", "LK-2"),
            Entity("Mātale", "LK-22", "DISTRICT", "si", "LK-2"),
            Entity("Māttaḷai", "LK-22", "DISTRICT", "ta", "LK-2"),
        ),
        "LK-23": (
            Entity("Nuvara Ĕliya", "LK-23", "DISTRICT", "si", "LK-2"),
            Entity("Nuvarĕliyā", "LK-23", "DISTRICT", "ta", "LK-2"),
            Entity("Nuwara Eliya", "LK-23", "DISTRICT", "en", "LK-2"),
        ),
        "LK-3": (
            Entity("Dakuṇu paḷāta", "LK-3", "PROVINCE", "si", ""),
            Entity("Southern Province", "LK-3", "PROVINCE", "en", ""),
            Entity("Tĕṉ mākāṇam", "LK-3", "PROVINCE", "ta", ""),
        ),
        "LK-31": (
            Entity("Galle", "LK-31", "DISTRICT", "en", "LK-3"),
            Entity("Gālla", "LK-31", "DISTRICT", "si", "LK-3"),
            Entity("Kāli", "LK-31", "DISTRICT", "ta", "LK-3"),
        ),
        "LK-32": (
            Entity("Matara", "LK-32", "DISTRICT", "en", "LK-3"),
            Entity("Mātara", "LK-32", "DISTRICT", "si", "LK-3"),
            Entity("Māttaṛai", "LK-32", "DISTRICT", "ta", "LK-3"),
        ),
        "LK-33": (
            Entity("Ampāntōṭṭai", "LK-33", "DISTRICT", "ta", "LK-3"),
            Entity("Hambantota", "LK-33", "DISTRICT", "en", "LK-3"),
            Entity("Hambantŏṭa", "LK-33", "DISTRICT", "si", "LK-3"),
        ),
        "LK-4": (
            Entity("Northern Province", "LK-4", "PROVINCE", "en", ""),
            Entity("Uturu paḷāta", "LK-4", "PROVINCE", "si", ""),
            Entity("Vaṭakku mākāṇam", "LK-4", "PROVINCE", "ta", ""),
        ),
        "LK-41": (
            Entity("Jaffna", "LK-41", "DISTRICT", "en", "LK-4"),
            Entity("Yāl̮ppāṇam", "LK-41", "DISTRICT", "ta", "LK-4"),
            Entity("Yāpanaya", "LK-41", "DISTRICT", "si", "LK-4"),
        ),
        "LK-42": (
            Entity("Kilinochchi", "LK-42", "DISTRICT", "en", "LK-4"),
            Entity("Kilinŏchchi", "LK-42", "DISTRICT", "si", "LK-4"),
            Entity("Kiḷinochchi", "LK-42", "DISTRICT", "ta", "LK-4"),
        ),
        "LK-43": (
            Entity("Mannar", "LK-43", "DISTRICT", "en", "LK-4"),
            Entity("Mannārama", "LK-43", "DISTRICT", "si", "LK-4"),
            Entity("Maṉṉār", "LK-43", "DISTRICT", "ta", "LK-4"),
        ),
        "LK-44": (
            Entity("Vavuniya", "LK-44", "DISTRICT", "en", "LK-4"),
            Entity("Vavuniyāva", "LK-44", "DISTRICT", "si", "LK-4"),
            Entity("Vavuṉiyā", "LK-44", "DISTRICT", "ta", "LK-4"),
        ),
        "LK-45": (
            Entity("Mulativ", "LK-45", "DISTRICT", "si", "LK-4"),
            Entity("Mullaittivu", "LK-45", "DISTRICT", "en", "LK-4"),
            Entity("Mullaittīvu", "LK-45", "DISTRICT", "ta", "LK-4"),
        ),
        "LK-5": (
            Entity("Eastern Province", "LK-5", "PROVINCE", "en", ""),
            Entity("Kil̮akku mākāṇam", "LK-5", "PROVINCE", "ta", ""),
            Entity("Næ̆gĕnahira paḷāta", "LK-5", "PROVINCE", "si", ""),
        ),
        "LK-51": (
            Entity("Batticaloa", "LK-51", "DISTRICT", "en", "LK-5"),
            Entity("Maḍakalapuva", "LK-51", "DISTRICT", "si", "LK-5"),
            Entity("Maṭṭakkaḷappu", "LK-51", "DISTRICT", "ta", "LK-5"),
        ),
        "LK-52": (
            Entity("Ampara", "LK-52", "DISTRICT", "en", "LK-5"),
            Entity("Ampāra", "LK-52", "DISTRICT", "si", "LK-5"),
            Entity("Ampāṟai", "LK-52", "DISTRICT", "ta", "LK-5"),
        ),
        "LK-53": (
            Entity("Tirukŏṇamalai", "LK-53", "DISTRICT", "ta", "LK-5"),
            Entity("Trikuṇāmalaya", "LK-53", "DISTRICT", "si", "LK-5"),
            Entity("Trincomalee", "LK-53", "DISTRICT", "en", "LK-5"),
        ),
        "LK-6": (
            Entity("North Western Province", "LK-6", "PROVINCE", "en", ""),
            Entity("Vayamba paḷāta", "LK-6", "PROVINCE", "si", ""),
            Entity("Vaṭamel mākāṇam", "LK-6", "PROVINCE", "ta", ""),
        ),
        "LK-61": (
            Entity("Kurunegala", "LK-61", "DISTRICT", "en", "LK-6"),
            Entity("Kurunākal", "LK-61", "DISTRICT", "ta", "LK-6"),
            Entity("Kuruṇægala", "LK-61", "DISTRICT", "si", "LK-6"),
        ),
        "LK-62": (
            Entity("Puttalam", "LK-62", "DISTRICT", "en", "LK-6"),
            Entity("Puttalama", "LK-62", "DISTRICT", "si", "LK-6"),
            Entity("Puttaḷam", "LK-62", "DISTRICT", "ta", "LK-6"),
        ),
        "LK-7": (
            Entity("North Central Province", "LK-7", "PROVINCE", "en", ""),
            Entity("Uturumæ̆da paḷāta", "LK-7", "PROVINCE", "si", ""),
            Entity("Vaṭamattiya mākāṇam", "LK-7", "PROVINCE", "ta", ""),
        ),
        "LK-71": (
            Entity("Anuradhapura", "LK-71", "DISTRICT", "en", "LK-7"),
            Entity("Anurādhapura", "LK-71", "DISTRICT", "si", "LK-7"),
            Entity("Anurātapuram", "LK-71", "DISTRICT", "ta", "LK-7"),
        ),
        "LK-72": (
            Entity("Polonnaruwa", "LK-72", "DISTRICT", "en", "LK-7"),
            Entity("Pŏlaṉṉaṛuvai", "LK-72", "DISTRICT", "ta", "LK-7"),
            Entity("Pŏḷŏnnaruva", "LK-72", "DISTRICT", "si", "LK-7"),
        ),
        "LK-8": (
            Entity("Uva Province", "LK-8", "PROVINCE", "en", ""),
            Entity("Ūva paḷāta", "LK-8", "PROVINCE", "si", ""),
            Entity("Ūvā mākāṇam", "LK-8", "PROVINCE", "ta", ""),
        ),
        "LK-81": (
            Entity("Badulla", "LK-81", "DISTRICT", "en", "LK-8"),
            Entity("Badulla", "LK-81", "DISTRICT", "si", "LK-8"),
            Entity("Patuḷai", "LK-81", "DISTRICT", "ta", "LK-8"),
        ),
        "LK-82": (
            Entity("Monaragala", "LK-82", "DISTRICT", "en", "LK-8"),
            Entity("Mŏṇarāgala", "LK-82", "DISTRICT", "si", "LK-8"),
            Entity("Mŏṉarākalai", "LK-82", "DISTRICT", "ta", "LK-8"),
        ),
        "LK-9": (
            Entity("Chappirakamuva mākāṇam", "LK-9", "PROVINCE", "ta", ""),
            Entity("Sabaragamuva paḷāta", "LK-9", "PROVINCE", "si", ""),
            Entity("Sabaragamuwa Province", "LK-9", "PROVINCE", "en", ""),
        ),
        "LK-91": (
            Entity("Irattiṉapuri", "LK-91", "DISTRICT", "ta", "LK-9"),
            Entity("Ratnapura", "LK-91", "DISTRICT", "en", "LK-9"),
            Entity("Ratnapura", "LK-91", "DISTRICT", "si", "LK-9"),
        ),
        "LK-92": (
            Entity("Kegalla", "LK-92", "DISTRICT", "en", "LK-9"),
            Entity("Kekālai", "LK-92", "DISTRICT", "ta", "LK-9"),
            Entity("Kægalla", "LK-92", "DISTRICT", "si", "LK-9"),
        ),
    }
