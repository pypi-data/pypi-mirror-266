from abc import (
    ABCMeta,
    abstractmethod,
)
from itertools import (
    chain,
)
from typing import (
    Optional,
)

from django.http.response import (
    JsonResponse,
)
from m3.actions import (
    Action,
    ActionPack,
)

from m3_gar_client.backends.m3_rest_gar.utils import (
    PlaceLoader,
    StreetLoader,
    UIHouseLoader,
    UISteadLoader,
)
from m3_gar_client.utils import (
    correct_keyboard_layout,
)


class ActionBase(Action, metaclass=ABCMeta):
    """
    Базовый класс для обработчиков запросов на поиск данных в ГАР.
    """

    # Признак того, что необходимо корректировать пользовательский ввод
    correct_keyboard_input = True

    @abstractmethod
    def _get_loader(self, context):
        """Возвращает загрузчик данных.

        :rtype: m3_gar_client.backends.m3_rest_gar.utils.LoaderBase
        """

    def context_declaration(self):
        return {
            'filter': {
                'type': 'unicode',
                'default': '',
            },
        }

    @staticmethod
    def get_page_number(context) -> Optional[int]:
        """Возвращает номер страницы из параметров запроса для загрузки данных.

        В ExtJs для постраничного получения данных используются параметры start и limit,
        тогда как в m3_rest_gar сервисе используется постраничный запрос с параметром page.
        Необходимо из значений start и limit определить номер страницы page.
        """
        start = getattr(context, 'start', None)
        limit = getattr(context, 'limit', None)
        page = None

        if start and limit:
            try:
                page = int(int(start) / int(limit)) + 1
            except (ZeroDivisionError, ValueError):
                page = 1

        return page

    def run(self, request, context):
        if self.correct_keyboard_input:
            context.filter = correct_keyboard_layout(context.filter)

        loader = self._get_loader(context)
        result = loader.load(page=self.get_page_number(context))

        return JsonResponse({
            'rows': result.rows,
            'total': result.total,
        })


class PlaceSearchAction(ActionBase):
    """
    Обработчик запросов на поиск населенных пунктов.
    """

    url = '/search/place'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return PlaceLoader(context.filter)


class ParentMixin:

    def context_declaration(self):
        result = super().context_declaration()

        result.update({
            'parent': {
                'type': 'unicode',
            },
        })

        return result


class StreetSearchAction(ParentMixin, ActionBase):
    """
    Обработчик запросов на поиск улиц в населенном пункте.
    """

    url = '/search/street'

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return StreetLoader(context.filter, parent_id=str(context.parent))


class HouseSearchAction(ParentMixin, ActionBase):
    """
    Обработчик запросов на поиск домов.
    """

    url = '/search/house'
    correct_keyboard_input = False

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return UIHouseLoader(context.filter, parent_id=context.parent)


class HouseOrSteadSearchAction(ParentMixin, ActionBase):
    """
    Обработчик запросов на поиск домов и земельных участков.
    """

    url = '/search/house_or_stead'
    correct_keyboard_input = False

    def run(self, request, context):
        if self.correct_keyboard_input:
            context.filter = correct_keyboard_layout(context.filter)

        loader_of_houses = self._get_loader(context)
        loader_of_steads = self.get_steads(context)

        house_result = loader_of_houses.load()
        stead_result = loader_of_steads.load()

        return JsonResponse({
            'rows': list(chain(house_result.rows, stead_result.rows)),
            'total': house_result.total + stead_result.total,
        })

    def _get_loader(self, context):
        # pylint: disable=abstract-class-instantiated
        return UIHouseLoader(context.filter, parent_id=context.parent)

    def get_steads(self, context):
        # pylint: disable=abstract-class-instantiated
        return UISteadLoader(context.filter, parent_id=context.parent)


class Pack(ActionPack):
    """
    Набор действий для проксирования запросов к серверу ГАР.
    """

    url = '/gar'

    def __init__(self):
        super().__init__()

        self.place_search_action = PlaceSearchAction()
        self.street_search_action = StreetSearchAction()
        self.house_search_action = HouseOrSteadSearchAction()

        self.actions.extend((
            self.place_search_action,
            self.street_search_action,
            self.house_search_action,
        ))
