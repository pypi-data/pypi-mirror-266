"""ISO 3166-2 BY standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:BY
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "BY-BR": (
            Entity("Bresckaja voblasć", "BY-BR", "OBLAST", "be", ""),
            Entity("Brestskaja oblast'", "BY-BR", "OBLAST", "ru", ""),
            Entity("Brestskaya oblast'", "BY-BR", "OBLAST", "ru", ""),
            Entity("Brestskaya voblasts'", "BY-BR", "OBLAST", "be", ""),
        ),
        "BY-HM": (
            Entity("Gorod Minsk", "BY-HM", "CITY", "ru", ""),
            Entity("Gorod Minsk", "BY-HM", "CITY", "ru", ""),
            Entity("Horad Minsk", "BY-HM", "CITY", "be", ""),
            Entity("Horad Minsk", "BY-HM", "CITY", "be", ""),
        ),
        "BY-HO": (
            Entity("Gomel'skaja oblast'", "BY-HO", "OBLAST", "ru", ""),
            Entity("Gomel'skaya oblast'", "BY-HO", "OBLAST", "ru", ""),
            Entity("Homieĺskaja voblasć", "BY-HO", "OBLAST", "be", ""),
            Entity("Homyel'skaya voblasts'", "BY-HO", "OBLAST", "be", ""),
        ),
        "BY-HR": (
            Entity("Grodnenskaja oblast'", "BY-HR", "OBLAST", "ru", ""),
            Entity("Grodnenskaya oblast'", "BY-HR", "OBLAST", "ru", ""),
            Entity("Hrodzienskaja voblasć", "BY-HR", "OBLAST", "be", ""),
            Entity("Hrodzyenskaya voblasts'", "BY-HR", "OBLAST", "be", ""),
        ),
        "BY-MA": (
            Entity("Mahilioŭskaja voblasć", "BY-MA", "OBLAST", "be", ""),
            Entity("Mahilyowskaya voblasts'", "BY-MA", "OBLAST", "be", ""),
            Entity("Mogilevskaja oblast'", "BY-MA", "OBLAST", "ru", ""),
            Entity("Mogilevskaya oblast'", "BY-MA", "OBLAST", "ru", ""),
        ),
        "BY-MI": (
            Entity("Minskaja oblast'", "BY-MI", "OBLAST", "ru", ""),
            Entity("Minskaja voblasć", "BY-MI", "OBLAST", "be", ""),
            Entity("Minskaya oblast'", "BY-MI", "OBLAST", "ru", ""),
            Entity("Minskaya voblasts'", "BY-MI", "OBLAST", "be", ""),
        ),
        "BY-VI": (
            Entity("Viciebskaja voblasć", "BY-VI", "OBLAST", "be", ""),
            Entity("Vitebskaja oblast'", "BY-VI", "OBLAST", "ru", ""),
            Entity("Vitebskaya oblast'", "BY-VI", "OBLAST", "ru", ""),
            Entity("Vitsyebskaya voblasts'", "BY-VI", "OBLAST", "be", ""),
        ),
    }
