"""A consolidated ISO 3166 based entities data.

It contains data from different ISO standards grouped by a specific entity.
"""

from importlib import import_module

from iso_standards.base import EntityCollection
from iso_standards.iso3166.iso3166_1 import Iso3166_1
from iso_standards.utils.types import Iso3166BasedEntity


class Iso3166BasedEntities(EntityCollection):
    __slots__ = ()

    entities = {}

    def __init__(self):
        super().__init__()

        for iso3166_1 in Iso3166_1():
            subdivisions = None
            try:
                subdivisions = getattr(
                    import_module(f"iso_standards.iso3166.iso3166_2.{iso3166_1.alpha_2}"),
                    "Iso3166_2",
                )()
            except ModuleNotFoundError:
                pass

            country = Iso3166BasedEntity(
                iso3166_1.short_name,
                iso3166_1.alpha_2,
                iso3166_1.alpha_3,
                iso3166_1.num_3,
                iso3166_1.long_name,
                iso3166_1.parent_code,
            )
            # Add additional attributes.
            country.subdivisions = subdivisions

            self.entities[iso3166_1.alpha_2] = country

    def __str__(self) -> str:
        return "ISO 3166"
