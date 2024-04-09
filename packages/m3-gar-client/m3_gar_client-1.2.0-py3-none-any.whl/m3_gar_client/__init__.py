from abc import (
    ABC,
)
from importlib import (
    import_module,
)

from django.conf import (
    settings,
)
# нужно для импорта констант отсюда в barsdoc
from m3_gar_constants import *

from m3_gar_client.utils import (
    cached_property,
)


default_app_config = f'{__package__}.apps.AppConfig'


class Config(ABC):

    """Базовый класс для конфигурации пакета."""

    @cached_property
    def backend(self):
        """Бэкенд для доступа к данным ГАР.

        :rtype: :class:`m3_gar_client.backends.base.BackendBase`
        """
        backend_class = import_module(settings.GAR['BACKEND']).Backend
        return backend_class()


#: Конфигурация приложения ``m3_gar_client``.
#:
#: Заполняется экземпляром класса :class:`m3_gar_client.Config`, либо его потомком,
#: при инициализации проекта *до* инициализации приложения ``m3-gar-client``.
config = None


if settings.DEBUG:
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
