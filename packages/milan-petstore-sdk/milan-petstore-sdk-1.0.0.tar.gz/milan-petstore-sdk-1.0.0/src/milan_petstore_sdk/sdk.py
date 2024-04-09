from .services.pets import PetsService
from .net.environment import Environment


class MilanPetstoreSdk:
    def __init__(self, base_url: str = Environment.DEFAULT.value):
        """
        Initializes MilanPetstoreSdk the SDK class.
        """
        self.pets = PetsService(base_url=base_url)

    def set_base_url(self, base_url):
        """
        Sets the base URL for the entire SDK.
        """
        self.pets.set_base_url(base_url)

        return self


# c029837e0e474b76bc487506e8799df5e3335891efe4fb02bda7a1441840310c
