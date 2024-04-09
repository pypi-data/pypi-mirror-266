from abc import ABC, abstractmethod


class Validate(ABC):
    def setup(self) -> None:
        """
        Sets up the connection for data validation.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """Abstract method to execute data extraction.

        Parameters:
            **kwargs: Arbitrary keyword arguments.
        """
        pass
