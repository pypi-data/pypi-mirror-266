from iso_standards.iso3166.types import Iso3166_1, Iso3166_2


class Iso3166BasedEntity(Iso3166_1):
    """ISO 3166 based lightweight immutable entity."""

    # Country subdivisions.
    subdivisions: Iso3166_2
