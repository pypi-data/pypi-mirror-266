from typing import List
from .utils.json_map import JsonMap
from .base import BaseModel


@JsonMap({"supported_countries": "supportedCountries"})
class Destinations(BaseModel):
    """Destinations

    :param name: Name of the destination, defaults to None
    :type name: str, optional
    :param destination: ISO representation of the destination, defaults to None
    :type destination: str, optional
    :param supported_countries: supported_countries, defaults to None
    :type supported_countries: List[str], optional
    """

    def __init__(
        self,
        name: str = None,
        destination: str = None,
        supported_countries: List[str] = None,
    ):
        self.name = name
        self.destination = destination
        self.supported_countries = supported_countries


@JsonMap({})
class ListDestinationsOkResponse(BaseModel):
    """ListDestinationsOkResponse

    :param destinations: destinations, defaults to None
    :type destinations: List[Destinations], optional
    """

    def __init__(self, destinations: List[Destinations] = None):
        self.destinations = self._define_list(destinations, Destinations)
