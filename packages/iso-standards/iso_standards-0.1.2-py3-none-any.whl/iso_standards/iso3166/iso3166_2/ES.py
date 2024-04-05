"""ISO 3166-2 ES standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ES
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ES-A": (
            Entity("Alacant", "ES-A", "PROVINCE", "ca", "ES-VC"),
            Entity("Alicante", "ES-A", "PROVINCE", "es", "ES-VC"),
        ),
        "ES-AB": (Entity("Albacete", "ES-AB", "PROVINCE", "es", "ES-CM"),),
        "ES-AL": (Entity("Almería", "ES-AL", "PROVINCE", "es", "ES-AN"),),
        "ES-AN": (Entity("Andalucía", "ES-AN", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-AR": (Entity("Aragón", "ES-AR", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-AS": (Entity("Asturias", "ES-AS", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-AV": (Entity("Ávila", "ES-AV", "PROVINCE", "es", "ES-CL"),),
        "ES-B": (Entity("Barcelona", "ES-B", "PROVINCE", "es", "ES-CT"),),
        "ES-BA": (Entity("Badajoz", "ES-BA", "PROVINCE", "es", "ES-EX"),),
        "ES-BI": (Entity("Bizkaia", "ES-BI", "PROVINCE", "eu", "ES-PV"),),
        "ES-BU": (Entity("Burgos", "ES-BU", "PROVINCE", "es", "ES-CL"),),
        "ES-C": (Entity("A Coruña", "ES-C", "PROVINCE", "gl", "ES-GA"),),
        "ES-CA": (Entity("Cádiz", "ES-CA", "PROVINCE", "es", "ES-AN"),),
        "ES-CB": (Entity("Cantabria", "ES-CB", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-CC": (Entity("Cáceres", "ES-CC", "PROVINCE", "es", "ES-EX"),),
        "ES-CE": (Entity("Ceuta", "ES-CE", "AUTONOMOUS CITY IN NORTH AFRICA", "es", ""),),
        "ES-CL": (Entity("Castilla y León", "ES-CL", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-CM": (Entity("Castilla-La Mancha", "ES-CM", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-CN": (Entity("Canarias", "ES-CN", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-CO": (Entity("Córdoba", "ES-CO", "PROVINCE", "es", "ES-AN"),),
        "ES-CR": (Entity("Ciudad Real", "ES-CR", "PROVINCE", "es", "ES-CM"),),
        "ES-CS": (
            Entity("Castelló", "ES-CS", "PROVINCE", "ca", "ES-VC"),
            Entity("Castellón", "ES-CS", "PROVINCE", "es", "ES-VC"),
        ),
        "ES-CT": (Entity("Catalunya", "ES-CT", "AUTONOMOUS COMMUNITY", "ca", ""),),
        "ES-CU": (Entity("Cuenca", "ES-CU", "PROVINCE", "es", "ES-CM"),),
        "ES-EX": (Entity("Extremadura", "ES-EX", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-GA": (Entity("Galicia", "ES-GA", "AUTONOMOUS COMMUNITY", "gl", ""),),
        "ES-GC": (Entity("Las Palmas", "ES-GC", "PROVINCE", "es", "ES-CN"),),
        "ES-GI": (Entity("Girona", "ES-GI", "PROVINCE", "ca", "ES-CT"),),
        "ES-GR": (Entity("Granada", "ES-GR", "PROVINCE", "es", "ES-AN"),),
        "ES-GU": (Entity("Guadalajara", "ES-GU", "PROVINCE", "es", "ES-CM"),),
        "ES-H": (Entity("Huelva", "ES-H", "PROVINCE", "es", "ES-AN"),),
        "ES-HU": (Entity("Huesca", "ES-HU", "PROVINCE", "es", "ES-AR"),),
        "ES-IB": (Entity("Illes Balears", "ES-IB", "AUTONOMOUS COMMUNITY", "ca", ""),),
        "ES-J": (Entity("Jaén", "ES-J", "PROVINCE", "es", "ES-AN"),),
        "ES-L": (Entity("Lleida", "ES-L", "PROVINCE", "ca", "ES-CT"),),
        "ES-LE": (Entity("León", "ES-LE", "PROVINCE", "es", "ES-CL"),),
        "ES-LO": (Entity("La Rioja", "ES-LO", "PROVINCE", "es", "ES-RI"),),
        "ES-LU": (Entity("Lugo", "ES-LU", "PROVINCE", "gl", "ES-GA"),),
        "ES-M": (Entity("Madrid", "ES-M", "PROVINCE", "es", "ES-MD"),),
        "ES-MA": (Entity("Málaga", "ES-MA", "PROVINCE", "es", "ES-AN"),),
        "ES-MC": (Entity("Murcia", "ES-MC", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-MD": (Entity("Madrid", "ES-MD", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-ML": (Entity("Melilla", "ES-ML", "AUTONOMOUS CITY IN NORTH AFRICA", "es", ""),),
        "ES-MU": (Entity("Murcia", "ES-MU", "PROVINCE", "es", "ES-MC"),),
        "ES-NA": (
            Entity("Nafarroa", "ES-NA", "PROVINCE", "eu", "ES-NC"),
            Entity("Navarra", "ES-NA", "PROVINCE", "es", "ES-NC"),
        ),
        "ES-NC": (
            Entity("Nafarroako Foru Komunitatea", "ES-NC", "AUTONOMOUS COMMUNITY", "eu", ""),
            Entity("Navarra", "ES-NC", "AUTONOMOUS COMMUNITY", "es", ""),
        ),
        "ES-O": (Entity("Asturias", "ES-O", "PROVINCE", "es", "ES-AS"),),
        "ES-OR": (Entity("Ourense", "ES-OR", "PROVINCE", "gl", "ES-GA"),),
        "ES-P": (Entity("Palencia", "ES-P", "PROVINCE", "es", "ES-CL"),),
        "ES-PM": (Entity("Illes Balears", "ES-PM", "PROVINCE", "ca", "ES-IB"),),
        "ES-PO": (Entity("Pontevedra", "ES-PO", "PROVINCE", "gl", "ES-GA"),),
        "ES-PV": (
            Entity("Euskal Herria", "ES-PV", "AUTONOMOUS COMMUNITY", "eu", ""),
            Entity("País Vasco", "ES-PV", "AUTONOMOUS COMMUNITY", "es", ""),
        ),
        "ES-RI": (Entity("La Rioja", "ES-RI", "AUTONOMOUS COMMUNITY", "es", ""),),
        "ES-S": (Entity("Cantabria", "ES-S", "PROVINCE", "es", "ES-CB"),),
        "ES-SA": (Entity("Salamanca", "ES-SA", "PROVINCE", "es", "ES-CL"),),
        "ES-SE": (Entity("Sevilla", "ES-SE", "PROVINCE", "es", "ES-AN"),),
        "ES-SG": (Entity("Segovia", "ES-SG", "PROVINCE", "es", "ES-CL"),),
        "ES-SO": (Entity("Soria", "ES-SO", "PROVINCE", "es", "ES-CL"),),
        "ES-SS": (Entity("Gipuzkoa", "ES-SS", "PROVINCE", "eu", "ES-PV"),),
        "ES-T": (Entity("Tarragona", "ES-T", "PROVINCE", "ca", "ES-CT"),),
        "ES-TE": (Entity("Teruel", "ES-TE", "PROVINCE", "es", "ES-AR"),),
        "ES-TF": (Entity("Santa Cruz de Tenerife", "ES-TF", "PROVINCE", "es", "ES-CN"),),
        "ES-TO": (Entity("Toledo", "ES-TO", "PROVINCE", "es", "ES-CM"),),
        "ES-V": (
            Entity("Valencia", "ES-V", "PROVINCE", "es", "ES-VC"),
            Entity("València", "ES-V", "PROVINCE", "ca", "ES-VC"),
        ),
        "ES-VA": (Entity("Valladolid", "ES-VA", "PROVINCE", "es", "ES-CL"),),
        "ES-VC": (
            Entity("Valenciana", "ES-VC", "AUTONOMOUS COMMUNITY", "es", ""),
            Entity("Valenciana", "ES-VC", "AUTONOMOUS COMMUNITY", "ca", ""),
        ),
        "ES-VI": (
            Entity("Araba", "ES-VI", "PROVINCE", "eu", "ES-PV"),
            Entity("Álava", "ES-VI", "PROVINCE", "es", "ES-PV"),
        ),
        "ES-Z": (Entity("Zaragoza", "ES-Z", "PROVINCE", "es", "ES-AR"),),
        "ES-ZA": (Entity("Zamora", "ES-ZA", "PROVINCE", "es", "ES-CL"),),
    }
