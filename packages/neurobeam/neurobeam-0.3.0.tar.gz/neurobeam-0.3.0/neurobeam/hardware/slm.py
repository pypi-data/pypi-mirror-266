from typing import Optional

from ..configs import HoistedConfig
from ..registries import Provider
from ..tools import HAS


@Provider()
class SLM:
    """
    SLM hardware class
    """

    def __init__(self,
                 config: Optional["HoistedConfig"] = None,
                 brand: str = "Meadowlark",
                 realtime_mode: bool = False):
        """
        SLM hardware class

        :param config: The hoisted configuration
        :param brand: The brand of the SLM (used only if config is not provided)
        :param realtime_mode: Whether the SLM is in realtime mode (used only if config is not provided)
        """
        #: Optional[HoistedConfig]: The hoisted configuration
        self.config = config
        #: str: The brand of the SLM
        self.brand = config.brand if HAS(config) else brand
        #: bool: The realtime mode of the SLM
        self.realtime_mode = config.realtime_mode if HAS(config) else realtime_mode

    def __str__(self) -> str:
        return f"SLM: {self.brand}, Realtime Mode: {self.realtime_mode}"

    def build(self) -> None:
        """
        Build the SLM
        """
        pass

    def start(self) -> None:
        """
        Start the SLM
        """
        pass

    def stop(self) -> None:
        """
        Stop the SLM
        """
        pass

    def destroy(self) -> None:
        """
        Destroy the SLM
        """
        pass
