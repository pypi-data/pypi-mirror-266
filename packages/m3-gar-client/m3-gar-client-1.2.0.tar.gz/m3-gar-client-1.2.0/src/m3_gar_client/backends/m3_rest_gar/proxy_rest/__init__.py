"""Бэкенд, проксирующий запросы через веб-приложение."""
from django.urls import (
    path,
)
from django.urls.base import (
    reverse,
)
from django.urls.conf import (
    include,
)
from django.utils.module_loading import (
    import_string,
)

from m3_gar_client.backends.m3_rest_gar.base import (
    BackendBase,
)

from . import (
    const,
)


class Backend(BackendBase):

    """REST-бэкенд для работы с сервером m3-rest-gar.

    .. code::python

      GAR = dict(
          BACKEND='m3_gar_client.backends.m3_rest_gar.proxy_rest',
          ...
      )

    """

    def init(self) -> None:
        from django.conf import (
            settings,
        )

        from m3_gar_client.utils import (
            reload_urlconf,
        )

        from .urls import (
            urlpatterns,
        )

        urlconf = import_string(f'{settings.ROOT_URLCONF}.urlpatterns')
        urlconf += [
            path(
                r'gar/',
                include('m3_gar_client.backends.m3_rest_gar.proxy_rest.urls')
            )
        ]

        reload_urlconf()

    @property
    def place_search_url(self) -> str:
        """URL для поиска населенных пунктов."""

        return reverse(const.SEARCH_PLACE_NAME)

    @property
    def street_search_url(self) -> str:
        """URL для поиска улиц."""

        return reverse(const.SEARCH_STREET_NAME)

    @property
    def house_search_url(self) -> str:
        """URL для запроса списка домов."""

        return reverse(const.SEARCH_HOUSE_OR_STEAD_NAME)

    @property
    def apartment_search_url(self) -> str:
        return reverse(const.SEARCH_APARTMENT)
