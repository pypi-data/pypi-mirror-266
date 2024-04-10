from typing import Optional

from anyscale._private.anyscale_client import (
    AnyscaleClient,
    AnyscaleClientInterface,
)
from anyscale.cli_logger import BlockLogger


class BaseSDK:
    """Shared parent class for all SDKs."""

    def __init__(
        self,
        *,
        logger: Optional[BlockLogger] = None,
        client: Optional[AnyscaleClientInterface] = None,
    ):
        self._logger = logger or BlockLogger()
        self._client = client or AnyscaleClient()

    @property
    def logger(self) -> BlockLogger:
        return self._logger

    @property
    def client(self) -> AnyscaleClientInterface:
        return self._client
