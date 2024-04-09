from .services.destinations import DestinationsService
from .services.packages import PackagesService
from .services.purchases import PurchasesService
from .services.e_sim import ESimService
from .net.environment import Environment


class Celitech:
    def __init__(self, base_url: str = Environment.DEFAULT.value):
        """
        Initializes Celitech the SDK class.
        """
        self.destinations = DestinationsService(base_url=base_url)
        self.packages = PackagesService(base_url=base_url)
        self.purchases = PurchasesService(base_url=base_url)
        self.e_sim = ESimService(base_url=base_url)

    def set_base_url(self, base_url):
        """
        Sets the base URL for the entire SDK.
        """
        self.destinations.set_base_url(base_url)
        self.packages.set_base_url(base_url)
        self.purchases.set_base_url(base_url)
        self.e_sim.set_base_url(base_url)

        return self


# c029837e0e474b76bc487506e8799df5e3335891efe4fb02bda7a1441840310c
