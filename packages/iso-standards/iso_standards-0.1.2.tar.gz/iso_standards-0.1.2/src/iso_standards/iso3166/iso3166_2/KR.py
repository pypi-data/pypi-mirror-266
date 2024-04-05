"""ISO 3166-2 KR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KR-11": (Entity("Seoul-teukbyeolsi", "KR-11", "SPECIAL CITY", "ko", ""),),
        "KR-26": (Entity("Busan-gwangyeoksi", "KR-26", "METROPOLITAN CITY", "ko", ""),),
        "KR-27": (Entity("Daegu-gwangyeoksi", "KR-27", "METROPOLITAN CITY", "ko", ""),),
        "KR-28": (Entity("Incheon-gwangyeoksi", "KR-28", "METROPOLITAN CITY", "ko", ""),),
        "KR-29": (Entity("Gwangju-gwangyeoksi", "KR-29", "METROPOLITAN CITY", "ko", ""),),
        "KR-30": (Entity("Daejeon-gwangyeoksi", "KR-30", "METROPOLITAN CITY", "ko", ""),),
        "KR-31": (Entity("Ulsan-gwangyeoksi", "KR-31", "METROPOLITAN CITY", "ko", ""),),
        "KR-41": (Entity("Gyeonggi-do", "KR-41", "PROVINCE", "ko", ""),),
        "KR-42": (
            Entity(
                "Gangwon-teukbyeoljachido", "KR-42", "SPECIAL SELF-GOVERNING PROVINCE", "ko", ""
            ),
        ),
        "KR-43": (Entity("Chungcheongbuk-do", "KR-43", "PROVINCE", "ko", ""),),
        "KR-44": (Entity("Chungcheongnam-do", "KR-44", "PROVINCE", "ko", ""),),
        "KR-45": (Entity("Jeollabuk-do", "KR-45", "PROVINCE", "ko", ""),),
        "KR-46": (Entity("Jeollanam-do", "KR-46", "PROVINCE", "ko", ""),),
        "KR-47": (Entity("Gyeongsangbuk-do", "KR-47", "PROVINCE", "ko", ""),),
        "KR-48": (Entity("Gyeongsangnam-do", "KR-48", "PROVINCE", "ko", ""),),
        "KR-49": (
            Entity("Jeju-teukbyeoljachido", "KR-49", "SPECIAL SELF-GOVERNING PROVINCE", "ko", ""),
        ),
        "KR-50": (Entity("Sejong", "KR-50", "SPECIAL SELF-GOVERNING CITY", "ko", ""),),
    }
