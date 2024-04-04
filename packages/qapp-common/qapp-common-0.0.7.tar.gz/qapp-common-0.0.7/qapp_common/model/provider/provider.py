"""
    QApp Platform Project provider.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from abc import abstractmethod, ABC

from ...enum.provider_tag import ProviderTag
from ...config.logging_config import logger


class Provider(ABC):

    def __init__(self, provider_type: ProviderTag):
        self.provider_type = provider_type

    @abstractmethod
    def get_backend(self, device_specification):
        """
        @param device_specification:
        """

        raise NotImplemented('[Provider] get_backend() method must be implemented')

    @abstractmethod
    def collect_provider(self):
        """

        """

        raise NotImplemented('[Provider] collect_provider() method must be implemented')

    def get_provider_type(self):
        logger.debug('[Provider] Get provider type')

        return self.provider_type
