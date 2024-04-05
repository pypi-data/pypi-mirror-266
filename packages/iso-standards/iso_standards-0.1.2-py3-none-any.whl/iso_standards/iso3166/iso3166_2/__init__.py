"""
ISO 3166-2 standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/glossary-for-iso-3166.html
  - https://www.iso.org/obp/ui/en/#iso:std:iso:3166:-2:ed-4:v1:en
  - https://www.iso.org/obp/ui/#search
"""

from importlib import import_module
from pathlib import Path

from iso_standards.base import EntityCollection


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {}

    def __init__(self):
        for module_name in sorted(Path(__file__).parent.rglob("??.py")):
            self.entities.update(
                getattr(
                    import_module(f"iso_standards.iso3166.iso3166_2.{module_name.stem}"),
                    "Iso3166_2",
                ).entities
            )

    def __str__(self) -> str:
        return "ISO 3166-2 entities"
