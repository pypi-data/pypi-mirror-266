"""Бэкенд, проксирующий запросы через веб-приложение."""
from uuid import (
    UUID,
)

from m3_gar_client.backends.m3_rest_gar.base import (
    BackendBase,
)


class Backend(BackendBase):
    """Бэкенд для работы с сервером m3-rest-gar."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._pack = None

    @staticmethod
    def _register_parsers():
        """Регистрация парсеров для параметров контекста."""

        from m3.actions.context import (
            DeclarativeActionContext,
        )

        params = (
            (
                'm3-gar:unicode-or-none',
                lambda s: str(s) if s else None
            ),
            (
                'm3-gar:int-list',
                lambda s: [int(x) for x in s.split(',')]
            ),
            (
                'm3-gar:guid-or-none',
                lambda x: UUID(x) if x else None
            ),
        )

        for name, parser in params:
            DeclarativeActionContext.register_parser(name, parser)

    def init(self):
        """Регистрирует наборы действий в M3."""

        from m3_gar_client import (
            config,
        )
        from m3_gar_client.backends.m3_rest_gar.proxy.actions import (
            Pack,
        )

        self._register_parsers()

        self._pack = Pack()

        config.controller.extend_packs((
            self._pack,
        ))

    def place_search_url(self):
        """URL для поиска населенных пунктов."""

        return self._pack.place_search_action.get_absolute_url()

    def street_search_url(self):
        """URL для поиска улиц."""

        return self._pack.street_search_action.get_absolute_url()

    def house_search_url(self):
        """URL для запроса списка домов."""

        return self._pack.house_search_action.get_absolute_url()
