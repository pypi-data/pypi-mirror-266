from abc import (
    ABC,
)
from typing import (
    List,
    Type,
)

from django.conf import (
    settings,
)
from django.utils.module_loading import (
    import_string,
)
from rest_framework.authentication import (
    BaseAuthentication,
)
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
from rest_framework.response import (
    Response,
)
from rest_framework.views import (
    APIView,
)

from m3_gar_client.backends.m3_rest_gar.utils import (
    LoaderBase,
    PlaceLoader,
    UIApartmentLoader,
    UIHouseLoader,
    UIHouseOrSteadLoader,
    UIStreetLoader,
)
from m3_gar_client.utils import (
    correct_keyboard_layout,
)

from .authentication import (
    CsrfExemptSessionAuthentication,
)


def __get_config_or_defaults(name, defaults):
    cfg = settings.GAR.get('REST', {}).get(name)
    if cfg is not None:
        return [import_string(path) for path in cfg]
    return defaults


def get_authentication_classes():
    return __get_config_or_defaults(
        'AUTHENTICATION_CLASSES', [CsrfExemptSessionAuthentication]
    )


def get_permission_classes():
    return __get_config_or_defaults(
        'PERMISSION_CLASSES', [IsAuthenticated]
    )


class AbstractSearchView(APIView, ABC):

    authentication_classes: List[Type[BaseAuthentication]] = (
        get_authentication_classes()
    )
    permission_classes: List[Type[BasePermission]] = (
        get_permission_classes()
    )

    # Признак того, что необходимо корректировать пользовательский ввод
    correct_keyboard_input = True
    loader_cls: Type[LoaderBase]

    def post(self, request):
        result = self._get_loader(request).load()

        return self._build_response(
            data=result.rows,
            total=result.total,
        )

    def _get_loader(self, request):
        """Возвращает инстанс загрузчика данных."""
        args, kwargs = self._get_loader_params(request)
        return self.loader_cls(*args, **kwargs)

    def _get_loader_params(self, request):
        filter_ = request.POST.get('filter', '')

        if self.correct_keyboard_input and filter_:
            filter_ = correct_keyboard_layout(filter_)

        return (filter_, ), {}

    def _build_response(self, data, total):
        return Response({
            'rows': data,
            'total': total,
        })


class ParentSearchMixin(AbstractSearchView):
    def _get_loader_params(self, request):
        args, kwargs = super()._get_loader_params(request)
        kwargs.update(parent_id=request.POST['parent'])
        return args, kwargs


class PlaceSearchView(AbstractSearchView):

    loader_cls = PlaceLoader


class StreetSearchView(ParentSearchMixin, AbstractSearchView):

    loader_cls = UIStreetLoader


class HouseSearchView(ParentSearchMixin, AbstractSearchView):

    correct_keyboard_input = False
    loader_cls = UIHouseLoader


class HouseOrSteadSearchView(ParentSearchMixin, AbstractSearchView):

    correct_keyboard_input = False
    loader_cls = UIHouseOrSteadLoader

    def post(self, request):
        result = self._get_loader(request).load()

        return self._build_response(
            data=result.rows,
            total=result.total,
        )


class ApartmentSearchView(ParentSearchMixin, AbstractSearchView):
    correct_keyboard_input = False
    loader_cls = UIApartmentLoader
