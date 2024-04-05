"""ISO 3166-2 NO standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NO
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NO-03": (
            Entity("Oslo", "NO-03", "COUNTY", "nn", ""),
            Entity("Oslo", "NO-03", "COUNTY", "nb", ""),
        ),
        "NO-11": (
            Entity("Rogaland", "NO-11", "COUNTY", "nn", ""),
            Entity("Rogaland", "NO-11", "COUNTY", "nb", ""),
        ),
        "NO-15": (
            Entity("Møre og Romsdal", "NO-15", "COUNTY", "nn", ""),
            Entity("Møre og Romsdal", "NO-15", "COUNTY", "nb", ""),
        ),
        "NO-18": (
            Entity("Nordland", "NO-18", "COUNTY", "nn", ""),
            Entity("Nordland", "NO-18", "COUNTY", "nb", ""),
        ),
        "NO-21": (
            Entity("Svalbard", "NO-21", "ARCTIC REGION", "nn", ""),
            Entity("Svalbard", "NO-21", "ARCTIC REGION", "nb", ""),
        ),
        "NO-22": (
            Entity("Jan Mayen", "NO-22", "ARCTIC REGION", "nn", ""),
            Entity("Jan Mayen", "NO-22", "ARCTIC REGION", "nb", ""),
        ),
        "NO-30": (
            Entity("Viken", "NO-30", "COUNTY", "nn", ""),
            Entity("Viken", "NO-30", "COUNTY", "nb", ""),
        ),
        "NO-34": (
            Entity("Innlandet", "NO-34", "COUNTY", "nn", ""),
            Entity("Innlandet", "NO-34", "COUNTY", "nb", ""),
        ),
        "NO-38": (
            Entity("Vestfold og Telemark", "NO-38", "COUNTY", "nn", ""),
            Entity("Vestfold og Telemark", "NO-38", "COUNTY", "nb", ""),
        ),
        "NO-42": (
            Entity("Agder", "NO-42", "COUNTY", "nn", ""),
            Entity("Agder", "NO-42", "COUNTY", "nb", ""),
        ),
        "NO-46": (
            Entity("Vestland", "NO-46", "COUNTY", "nn", ""),
            Entity("Vestland", "NO-46", "COUNTY", "nb", ""),
        ),
        "NO-50": (
            Entity("Trööndelage", "NO-50", "COUNTY", "", ""),
            Entity("Trøndelag", "NO-50", "COUNTY", "nn", ""),
            Entity("Trøndelag", "NO-50", "COUNTY", "nb", ""),
        ),
        "NO-54": (
            Entity("Romssa ja Finnmárkku", "NO-54", "COUNTY", "se", ""),
            Entity("Troms og Finnmark", "NO-54", "COUNTY", "nn", ""),
            Entity("Troms og Finnmark", "NO-54", "COUNTY", "nb", ""),
            Entity("Tromssan ja Finmarkun", "NO-54", "COUNTY", "", ""),
        ),
    }
