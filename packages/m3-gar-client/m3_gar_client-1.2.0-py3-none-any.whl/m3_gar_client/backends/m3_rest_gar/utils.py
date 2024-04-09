import http.client as http_client
from abc import (
    ABC,
    abstractmethod,
)
from itertools import (
    chain,
    count,
)
from typing import (
    Generator,
    List,
    NamedTuple,
    Optional,
    Tuple,
)

from m3_gar_constants import (
    DEFAULT_PAGE_LIMIT,
    GAR_HIERARCHY_MUN,
    GAR_LEVELS_PLACE,
    GAR_LEVELS_STREET,
)

from m3_gar_client.backends.m3_rest_gar.server import (
    server,
)
from m3_gar_client.data import (
    AddressObject,
    Apartment,
    House,
    ObjectMapper,
    Stead,
)
from m3_gar_client.utils import (
    cached_property,
)


# -----------------------------------------------------------------------------
# Обёртки над данными, поступающими с сервера m3-rest-gar.

class AddressObjectMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar об адресных объектах.

    Предназначена для использования при создании экземпляров.
    """

    fields_map = {
        'id': 'id',
        'guid': 'objectguid',
        'obj_id': 'objectid',
        'previous_id': 'previd',
        'next_id': 'nextid',
        'ifns_fl_code': 'params__IFNSFL__value',
        'ifns_fl_territorial_district_code': 'params__territorialifnsflcode__value',
        'ifns_ul_code': 'params__IFNSUL__value',
        'ifns_ul_territorial_district_code': 'params__territorialifnsulcode__value',
        'okato': 'params__OKATO__value',
        'oktmo': 'params__OKTMO__value',
        'postal_code': 'params__PostIndex__value',
        'formal_name': 'name',
        'official_name': 'name',
        'short_name': 'typename',
        'type_full_name': 'type_full_name',
        'level': 'level',
        'kladr_code': 'params__CODE__value',
        'kladr_plain_code': 'params__PLAINCODE__value',
        'date_of_update': 'updatedate',
        'date_of_creation': 'startdate',
        'date_of_expiration': 'enddate',
        'full_name': 'hierarchy__mun__name_with_parents',
        'has_children': 'hierarchy__mun__has_children',
        'region_code': 'region_code',
        'adm_parent_obj_id': 'hierarchy__adm__parentobjid__objectid',
        'adm_parent_guid': 'hierarchy__adm__parentobjid__objectguid',
        'mun_parent_obj_id': 'hierarchy__mun__parentobjid__objectid',
        'mun_parent_guid': 'hierarchy__mun__parentobjid__objectguid',
    }

    assert set(fields_map) == set(AddressObject.fields)


class HouseMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar об адресных объектах.

    Предназначена для использования при создании экземпляров.
    """

    fields_map = {
        'id': 'id',
        'guid': 'objectguid',
        'obj_id': 'objectid',
        'ifns_fl_code': 'params__IFNSFL__value',
        'ifns_fl_territorial_district_code': 'params__territorialifnsflcode__value',
        'ifns_ul_code': 'params__IFNSUL__value',
        'ifns_ul_territorial_district_code': 'params__territorialifnsulcode__value',
        'okato': 'params__OKATO__value',
        'oktmo': 'params__OKTMO__value',
        'postal_code': 'params__PostIndex__value',
        'house_number': 'housenum',
        'building_number': 'addnum1',
        'structure_number': 'addnum2',
        'date_of_update': 'updatedate',
        'date_of_creation': 'startdate',
        'date_of_end': 'enddate',
        'region_code': 'region_code',
        'adm_parent_obj_id': 'hierarchy__adm__parentobjid__objectid',
        'adm_parent_guid': 'hierarchy__adm__parentobjid__objectguid',
        'mun_parent_obj_id': 'hierarchy__mun__parentobjid__objectid',
        'mun_parent_guid': 'hierarchy__mun__parentobjid__objectguid',
        'level': 'hierarchy__mun__objectid__levelid',
        'number': 'number',
        'house_type': 'housetype__shortname',
        'house_type_full': 'housetype__name',
        'building_type': 'addtype1__shortname',
        'building_type_full': 'addtype1__name',
        'structure_type': 'addtype2__shortname',
        'structure_type_full': 'addtype2__name',
    }

    assert set(fields_map) == set(House.fields)


class SteadMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar об адресных объектах."""

    fields_map = {
        'id': 'id',
        'guid': 'objectguid',
        'obj_id': 'objectid',
        'ifns_fl_code': 'params__IFNSFL__value',
        'ifns_fl_territorial_district_code': 'params__territorialifnsflcode__value',
        'ifns_ul_code': 'params__IFNSUL__value',
        'ifns_ul_territorial_district_code': 'params__territorialifnsulcode__value',
        'okato': 'params__OKATO__value',
        'oktmo': 'params__OKTMO__value',
        'postal_code': 'params__PostIndex__value',
        'house_number': 'number',
        'date_of_update': 'updatedate',
        'date_of_creation': 'startdate',
        'date_of_end': 'enddate',
        'region_code': 'region_code',
        'adm_parent_obj_id': 'hierarchy__adm__parentobjid__objectid',
        'adm_parent_guid': 'hierarchy__adm__parentobjid__objectguid',
        'mun_parent_obj_id': 'hierarchy__mun__parentobjid__objectid',
        'mun_parent_guid': 'hierarchy__mun__parentobjid__objectguid',
        'level': 'hierarchy__mun__objectid__levelid',
        'number': 'number',
    }


class ApartmentMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar о помещениях."""

    fields_map = {
        'id': 'id',
        'guid': 'objectguid',
        'obj_id': 'objectid',
        'number': 'number',
        'apart_type_full': 'aparttype__name',
        'apart_type': 'aparttype__shortname',
        'adm_parent_obj_id': 'hierarchy__adm__parentobjid__objectid',
        'adm_parent_guid': 'hierarchy__adm__parentobjid__objectguid',
        'mun_parent_obj_id': 'hierarchy__mun__parentobjid__objectid',
        'mun_parent_guid': 'hierarchy__mun__parentobjid__objectguid',
        'level': 'hierarchy__mun__objectid__levelid',
    }


class UIAddressObjectMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar об адресных объектах.

    Предназначена для использования в UI.
    """

    fields_map = {
        'objectId': 'objectguid',
        'level': 'level',
        'shortName': 'typename',
        'typeFullName': 'type_full_name',
        'formalName': 'name',
        'postalCode': 'params__PostIndex__value',
        'fullName': 'hierarchy__mun__name_with_parents',    # оставлено для совместимости
        'displayName': 'hierarchy__mun__name_with_parents',
        'hasChildren': 'hierarchy__mun__has_children',
    }


class UIStreetMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar об улицах.

    Предназначена для использования в UI.
    """

    fields_map = {
        'objectId': 'objectguid',
        'level': 'level',
        'shortName': 'typename',
        'typeFullName': 'type_full_name',
        'formalName': 'name',
        'postalCode': 'params__PostIndex__value',
        'displayName': 'name_with_typename',
    }


class UIHouseMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar о зданиях.

    Предназначена для использования в UI.
    """

    @staticmethod
    def _get_display_name(drf_object_data):
        type_number_mapping = {
            'housetype__shortname': 'housenum',
            'addtype1__shortname': 'addnum1',
            'addtype2__shortname': 'addnum2',
        }
        parts = (
            f'{drf_object_data.get(k)} {drf_object_data.get(v)}'
            for k, v in type_number_mapping.items()
            if all((drf_object_data.get(k), drf_object_data.get(v)))
        )
        return ', '.join(parts)

    fields_map = {
        'objectId': 'objectguid',
        'houseNumber': 'housenum',
        'buildingNumber': 'addnum1',
        'structureNumber': 'addnum2',
        'postalCode': 'params__PostIndex__value',
        'houseType': 'housetype__shortname',
        'buildingType': 'addtype1__shortname',
        'structureType': 'addtype2__shortname',
        'displayName': _get_display_name,
    }


class UISteadMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar о земельных участках.

    Предназначена для использования в UI.
    """

    fields_map = {
        'objectId': 'objectguid',
        'steadNumber': 'number',
        'postalCode': 'params__PostIndex__value',
    }


class UIApartmentMapper(ObjectMapper):
    """Обертка над данными сервера m3-rest-gar о помещениях.

    Предназначена для использования в UI.
    """

    @staticmethod
    def _get_display_name(drf_object_data):
        apartment_number = drf_object_data.get('number')
        apart_type = drf_object_data.get('aparttype__shortname')

        if apart_type:
            full_name = f'{apart_type} {apartment_number}'
        else:
            full_name = apartment_number

        return full_name

    fields_map = {
        'objectId': 'objectguid',
        'number': 'number',
        'apartType': 'aparttype__shortname',
        'displayName': _get_display_name,
    }


# -----------------------------------------------------------------------------
# Загрузчики данных с сервера m3-rest-gar.

class LoaderResult(NamedTuple):
    """Результат загрузки данных."""

    rows: List[dict]
    total: int


class LoaderBase(ABC):
    """Базовый класс для загрузчиков объектов ГАР.

    Attributes:
        filter_string: Строка для фильтрации объектов.
        timeout: Timeout запросов к серверу ГАР в секундах.
    """

    def __init__(self, filter_string, **kwargs):
        self.filter_string = filter_string
        self.timeout = kwargs.get('timeout')
        self.exact = kwargs.get('exact', False)

    @property
    @abstractmethod
    def _path(self):
        """Путь к ресурсу API сервера ГАР."""

    @cached_property
    def _fields(self):
        """Имена полей, подлежащих загрузке."""

        return list(self._mapper_class.fields_map.keys())

    @property
    @abstractmethod
    def _mapper_class(self):
        """Класс, преобразующий имена полей."""

    @property
    def _filter_param(self):
        """Query-параметр для фильтрации."""

        return 'name'

    def _load_page(self, params, page):
        params = params.copy()
        params['page'] = page

        drf_response = server.get(self._path, params, timeout=self.timeout)
        if drf_response and drf_response.status_code == http_client.OK:
            result = drf_response.json()
        else:
            result = None

        return result

    def _process_object_data(self, drf_object_data):
        """Выполняет дополнительную обработку данных объекта ГАР.

        Args:
            drf_object_data: Данные объекта ГАР, полученные с сервера m3-rest-gar.
        """
        return map_object_data(self._mapper_class, drf_object_data)

    def _build_result(self, object_data):
        """Формирует данные результирующего объекта ГАР.

        Полученные данные включаются в результат загрузки.

        Args:
            object_data: Данные объекта, полученные с сервера ГАР и прошедшие обработку в методе
                         ``_process_object_data``.
        """

        return {field: object_data[field] for field in self._fields}

    @abstractmethod
    def _filter(self, object_data):
        """Возвращает True, если объект ГАР должен попасть в загрузку."""

    def _get_params(self):
        """Возвращает параметры запроса к серверу ГАР."""

        filter_param = self._filter_param

        if self.exact:
            filter_param += '__exact'

        result = {
            filter_param: self.filter_string,
        }

        return result

    def load_raw_page(self, page_number: int, params: Optional[dict] = None) -> Tuple[Generator, bool, int]:
        """Возвращает данные конкретной страницы адресных объектов в исходном виде.

        Также возвращает признак наличия следующей страницы с данными и общее число найденных объектов.
        """
        if params is None:
            params = self._get_params()

        results = ()
        total_count = 0
        has_next_page = False

        drf_data = self._load_page(params, page_number)

        if drf_data:
            total_count = drf_data['count']
            results = drf_data['results']
            has_next_page = drf_data.get('next') or False

        result_data = (
            object_data
            for object_data in (self._process_object_data(drf_data) for drf_data in results)
            if self._filter(object_data)
        )

        return result_data, has_next_page, total_count

    def load_raw(self, page: Optional[int] = None) -> Generator:
        """Возвращает данные адресных объектов в исходном виде.

        Args:
            page: Номера страницы для загрузки данных. ``None`` указывает на необходимость загрузки всех страниц.
        """

        from django.conf import (
            settings,
        )

        page_limit = settings.GAR.get('PAGE_LIMIT', DEFAULT_PAGE_LIMIT)

        if page is None:
            pages = count(start=1)
        else:
            pages = range(page, page + 1)

        params = self._get_params()

        for page_number in pages:
            result_data, has_next_page, total_count = self.load_raw_page(page_number, params)

            yield from result_data

            if not has_next_page or page_number >= page_limit:
                break

    def load_page_results(self, page_number: int) -> Tuple[Generator, int]:
        """Возвращает данные в соответствии с параметрами загрузчика по указанной странице."""
        result_data, _, total_count = self.load_raw_page(page_number)

        return (self._build_result(data) for data in result_data), total_count

    def load_results(self, page=None):
        """Возвращает данные в соответствии с параметрами загрузчика.

        Args:
            page: Номера страницы для загрузки данных. ``None`` указывает на необходимость загрузки всех страниц.
        """

        return map(self._build_result, self.load_raw(page))

    @abstractmethod
    def _sort_key(self, object_data):
        """Возвращает значение ключа для сортировки результатов загрузки.

        Args:
            object_data: Данные загруженного объекта ГАР.
        """

    def _process_result(self, data):
        """Обработка полученных после загрузки данных.

        Args:
            data: Кортеж словарей с данными загруженных объектов ГАР.
        """

        return sorted(data, key=self._sort_key)

    def load(self, page: Optional[int] = None) -> LoaderResult:
        """Загружает данные с сервера ГАР.

        Args:
            page: Номера страницы для загрузки данных. ``None`` указывает на необходимость загрузки всех страниц.
        """
        if page is None:
            data = self.load_results()
            total = None
        else:
            data, total = self.load_page_results(page)

        rows = self._process_result(data)
        total = total or len(rows)

        return LoaderResult(rows=rows, total=total)


class ParentFilterMixin:
    """Миксин для загрузчиков, которые используют id родительского объекта в запросах к серверу ГАР."""

    @property
    @abstractmethod
    def _default_hierarchy(self):
        """Вид иерархии, используемый по умолчанию."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._hierarchy = kwargs.get('hierarchy') or self._default_hierarchy
        self._parent_id = kwargs.get('parent_id')

    def _get_params(self):
        result = super()._get_params()

        if self._parent_id:
            result['parent'] = str('{}:{}'.format(self._hierarchy, self._parent_id))

        return result


class AddressObjectLoaderBase(ParentFilterMixin, LoaderBase):
    """Базовый класс для загрузчиков адресных объектов ГАР.

    В терминологии ГАР адресными объектами называются:

        * субъекты РФ;
        * административные и муниципальные районы субъектов РФ;
        * города;
        * сельские/городские поселения;
        * населенные пункты;
        * элементы планировочной структуры;
        * улицы.
    """

    _default_hierarchy = GAR_HIERARCHY_MUN

    @property
    def _path(self):
        return '/addrobj/'

    @property
    @abstractmethod
    def _levels(self):
        """Уровни адресных объектов, для которых нужно искать данные в ГАР."""

    def _get_params(self):
        """Возвращает параметры запроса к серверу ГАР."""

        result = super()._get_params()

        if self._levels:
            result['level'] = ','.join(map(str, self._levels))

        return result

    def _filter(self, object_data):
        return True

    def _sort_key(self, object_data):
        return object_data['fullName'] or ''


class AddressObjectLoader(AddressObjectLoaderBase):
    """Загрузчик адресных объектов ГАР.

    Загружает информацию об адресных объектах, соответствующих строке
    фильтрации и находящихся на одном из указанных в параметрах экземпляра
    уровней иерархии адресных объектов.
    """

    _levels = None

    _mapper_class = AddressObjectMapper

    def __init__(self, filter_string, levels=None, typenames=None, **kwargs):
        """Инициализация экземпляра класса.

        Args:
            filter_string: Строка для фильтрации объектов.
            levels: Уровни адресных объектов.
        """

        super().__init__(filter_string, **kwargs)

        self._levels = levels
        self._typenames = typenames

    def _get_params(self):
        result = super()._get_params()

        if self._typenames:
            result['typename'] = ','.join(map(str, self._typenames))

        return result


class PlaceLoader(AddressObjectLoaderBase):
    """Загрузчик сведений о населенных пунктах."""

    _levels = GAR_LEVELS_PLACE

    _mapper_class = UIAddressObjectMapper

    @property
    def _filter_param(self):
        """Query-параметр для фильтрации."""

        return 'name_with_parents'

    def _get_params(self):
        """Возвращает параметры запроса к серверу ГАР."""

        filter_param = self._filter_param

        if self.exact:
            filter_param += '__exact'

        result = {
            filter_param: f'{self._default_hierarchy}:{self.filter_string}',
        }

        return result

    def _filter(self, object_data):
        return bool(object_data['fullName'])

    def _sort_key(self, object_data):
        return object_data['level'], object_data['fullName'] or ''


class StreetLoader(AddressObjectLoaderBase):
    """Загрузчик сведений об улицах."""

    _levels = GAR_LEVELS_STREET

    _mapper_class = UIAddressObjectMapper

    @property
    def _filter_param(self):
        """Query-параметр для фильтрации."""

        return 'name_with_typename'


class HouseLoader(ParentFilterMixin, LoaderBase):
    """Загрузчик сведений о зданиях."""

    _default_hierarchy = GAR_HIERARCHY_MUN

    _mapper_class = HouseMapper

    @property
    def _path(self):
        return '/houses/'

    @property
    def _filter_param(self):
        return 'housenum'

    def _filter(self, object_data):
        return True

    def _sort_key(self, object_data):
        return object_data['house_number'] or ''

    @staticmethod
    def _split_number(number):
        """Разделяет номер на целочисленную и буквенную части.

        Args:
            number: Номер дома/корпуса/строения.
        """

        int_part = ''.join(ch for ch in number if ch.isdigit())
        str_part = number[len(int_part):]

        return int(int_part) if int_part else -1, str_part


class SteadLoader(ParentFilterMixin, LoaderBase):
    """Загрузчик сведений о земельных участках."""

    _default_hierarchy = GAR_HIERARCHY_MUN

    _mapper_class = SteadMapper

    @property
    def _path(self):
        return '/steads/'

    @property
    def _filter_param(self):
        return 'number'

    def _filter(self, object_data):
        return True

    def _sort_key(self, object_data):
        return object_data.get('stead_number', object_data.get('number')) or ''

    @staticmethod
    def _split_number(number):
        """Разделяет номер на целочисленную и буквенную части.

        Args:
            number: Номер земельного участка.
        """

        int_part = ''.join(ch for ch in number if ch.isdigit())
        str_part = number[len(int_part):]

        return int(int_part) if int_part else -1, str_part


class ApartmentLoader(ParentFilterMixin, LoaderBase):
    """Загрузчик сведений о помещениях."""

    _default_hierarchy = GAR_HIERARCHY_MUN

    _mapper_class = ApartmentMapper

    @property
    def _path(self):
        return '/apartments/'

    @property
    def _filter_param(self):
        return 'number'

    def _filter(self, object_data):
        return True

    def _sort_key(self, object_data):
        return object_data['number'] or ''

    @staticmethod
    def _split_number(number):
        """Разделяет номер на целочисленную и буквенную части.

        Args:
            number: Номер земельного участка.
        """

        int_part = ''.join(ch for ch in number if ch.isdigit())
        str_part = number[len(int_part):]

        return int(int_part) if int_part else -1, str_part


class UIStreetLoader(StreetLoader):
    _mapper_class = UIStreetMapper

    def _sort_key(self, object_data):
        return object_data['displayName']


class UIHouseLoader(HouseLoader):
    _mapper_class = UIHouseMapper

    def _sort_key(self, object_data):
        return tuple(chain(*(
            self._split_number(object_data[number_type + 'Number'])
            for number_type in ('house', 'building', 'structure')
        )))

    def _filter(self, object_data):
        """Возвращает True для записей, соответствующих параметрам поиска.

        Запись считается соответствующей указанным при инициализации загрузчика
        параметрам поиска, если:

            * номер дома (если есть) в записи **начинается со строки**,
              указанной в аргументе ``filter_string``;
            * номер корпуса или строения (если номер дома отсутствует) в записи
              **начинается со строки**, указанной в аргументе
              ``filter_string``;
            * в аргументе ``filter_string`` конструктора класса было передано
              значение ``None``.
        """
        filter_string_lower = self.filter_string.lower()

        if self.filter_string is None:
            result = True
        else:
            house = (object_data.get('houseNumber') or '').lower()

            if house:
                result = house.startswith(filter_string_lower)
            else:
                building = (object_data.get('buildingNumber') or '').lower()
                structure = (object_data.get('structureNumber') or '').lower()
                result = (
                    (building and building.startswith(filter_string_lower)) or
                    (structure and structure.startswith(filter_string_lower))
                )

        return result

    def _process_object_data(self, drf_object_data):
        house_data = super()._process_object_data(drf_object_data)

        house_data['houseNumber'] = house_data['houseNumber'] or ''
        house_data['buildingNumber'] = house_data['buildingNumber'] or ''
        house_data['structureNumber'] = house_data['structureNumber'] or ''

        return house_data


class UISteadLoader(SteadLoader):
    _mapper_class = UISteadMapper

    def _sort_key(self, object_data):
        return tuple(chain(*(
            self._split_number(object_data[number_type + 'Number'])
            for number_type in ('stead',)
        )))

    def _filter(self, object_data):
        """Возвращает True для записей, соответствующих параметрам поиска.

        Запись считается соответствующей указанным при инициализации загрузчика
        параметрам поиска, если:

            * номер участка в записи **начинается со строки**,
              указанной в аргументе ``filter_string``;
            * в аргументе ``filter_string`` конструктора класса было передано
              значение ``None``.
        """

        filter_string_lower = self.filter_string.lower()

        if self.filter_string is None:
            result = True
        else:
            stead = (object_data.get('steadNumber') or '').lower()
            result = stead.startswith(filter_string_lower)

        return result

    def _process_object_data(self, drf_object_data):
        stead_data = super()._process_object_data(drf_object_data)

        stead_data['steadNumber'] = stead_data['steadNumber'] or ''

        return stead_data


class UIHouseOrSteadLoader:

    """Фасад для загрузки домов и участков."""

    def __init__(self, *args, **kwargs):
        self._house_loader = UIHouseLoader(*args, **kwargs)
        self._stead_loader = UISteadLoader(*args, **kwargs)

    def load(self, page: Optional[int] = None) -> LoaderResult:
        house_result = self._house_loader.load(page=page)
        stead_result = self._stead_loader.load(page=page)
        total = house_result.total + stead_result.total

        return LoaderResult(
            rows=list(chain(house_result.rows, stead_result.rows)),
            total=total,
        )


class UIApartmentLoader(ApartmentLoader):

    _mapper_class = UIApartmentMapper


# -----------------------------------------------------------------------------
# Функции для создания объектов m3-gar-client на основе данных m3-rest-gar.
def get_address_object(obj_id, timeout=None):
    """Возвращает адресный объект, загруженный с сервера ГАР.

    Если адресный объект не найден, возвращает ``None``.

    Args:
        obj_id: ObjectID/GUID адресного объекта ГАР.
        timeout: timeout запроса к серверу ГАР в секундах.

    Returns:
        Адресный объект

    Exceptions:
        requests.ConnectionError: если не удалось соединиться с сервером ГАР
    """
    address_object = None

    if obj_id:
        response = server.get('/addrobj/{}/'.format(obj_id), timeout=timeout)

        if response and response.status_code == http_client.OK:
            response_data = response.json()
            mapped_data = map_object_data(AddressObjectMapper, response_data)
            address_object = AddressObject(**mapped_data)

    return address_object


def find_address_objects(
    filter_string,
    levels=None,
    typenames=None,
    parent_id=None,
    timeout=None,
):
    """Возвращает адресные объекты, соответствующие параметрам поиска.

    Args:
        filter_string: Строка поиска.
        levels: Уровни адресных объектов, среди которых нужно осуществлять поиск.
        parent_id: ID родительского объекта.
        timeout: Timeout запросов к серверу ГАР в секундах.
    """

    return AddressObjectLoader(
        filter_string,
        levels=levels,
        typenames=typenames,
        parent_id=parent_id,
        timeout=timeout,
    ).load_results()


def get_stead(stead_id, timeout=None):
    """
    Возвращает информацию о земельном участке по его ID в ГАР.

    Args:
        stead_id: ID земельного участка.
        timeout: Timeout запросов к серверу ГАР в секундах.

    Returns:
        Объект m3_gar_client.data.Stead
    """

    assert stead_id is not None

    response = server.get('/steads/{}/'.format(stead_id), timeout=timeout)

    if response and response.status_code == http_client.OK:
        response_data = response.json()
        mapped_data = map_object_data(SteadMapper, response_data)
        stead = Stead(**mapped_data)
    else:
        stead = None

    return stead


def get_house(house_id, timeout=None):
    """Возвращает информацию о здании по его ID в ГАР.

    Args:
        house_id: ID здания.
        timeout: Timeout запросов к серверу ГАР в секундах.
    """

    assert house_id is not None

    response = server.get('/houses/{}/'.format(house_id), timeout=timeout)

    if response and response.status_code == http_client.OK:
        response_data = response.json()
        mapped_data = map_object_data(HouseMapper, response_data)
        result = House(**mapped_data)
    else:
        result = None

    return result


def find_house(house_number='', parent_id=None, building_number=None, structure_number=None, timeout=None):
    """Возвращает информацию о здании по его номеру.

    Args:
        house_number: Номер дома.
        parent_id: ID родительского объекта.
        building_number: Номер корпуса.
        structure_number: Номер строения.
        timeout: Timeout запросов к серверу ГАР в секундах.
    """

    result = HouseLoader(
        house_number,
        parent_id=parent_id,
        exact=True,
        timeout=timeout,
    ).load()

    houses = result.rows

    if len(houses) > 1:
        _filter = lambda house: (
            house['building_number'] == building_number and
            house['structure_number'] == structure_number
        )
        houses = list(filter(_filter, houses))

    if len(houses) == 1:
        house = House(**houses[0])
    else:
        house = None

    return house


def find_stead(number='', parent_id=None, timeout=None):
    """Возвращает информацию об участке по его номеру.

    :param str number: Номер участка.
    :param parent_id: ID родительского объекта.
    :param float timeout: Timeout запросов к серверу ГАР в секундах.

    :rtype: m3_gar_client.data.Stead or NoneType
    """
    result = SteadLoader(
        number,
        parent_id=parent_id,
        timeout=timeout,
    ).load()

    steads = result.rows

    if len(steads) == 1:
        stead = Stead(**steads[0])
    else:
        stead = None

    return stead


def get_apartment(apartment_id, timeout=None):
    """Возвращает информацию о помещении по его ID в ГАР.

    Args:
        apartment_id: ID помещения.
        timeout: Timeout запросов к серверу ГАР в секундах.
    """
    assert apartment_id is not None

    response = server.get('/apartments/{}/'.format(apartment_id), timeout=timeout)

    if response and response.status_code == http_client.OK:
        response_data = response.json()
        mapped_data = map_object_data(ApartmentMapper, response_data)
        apartment = Apartment(**mapped_data)
    else:
        apartment = None

    return apartment


def find_apartment(number='', parent_id=None, timeout=None):
    """Возвращает информацию о помещении по его номеру.

    Args:
        number: Номер квартиры.
        parent_id: ID родительского объекта.
        timeout: Timeout запросов к серверу ГАР в секундах.
    """

    result = ApartmentLoader(
        number,
        parent_id=parent_id,
        exact=True,
        timeout=timeout,
    ).load()

    apartments = result.rows

    if len(apartments) == 1:
        apartment = Apartment(**apartments[0])
    else:
        apartment = None

    return apartment


def flatten_object_data(raw_object_data):
    """Преобразует данные объекта ГАР к "плоскому" виду.

    Args:
        raw_object_data: Необработанные данные объекта ГАР, полученные с сервера m3-rest-gar.
    """

    flat_data = {}

    for key, value in raw_object_data.items():
        if type(value) is dict:
            for inner_key, inner_value in flatten_object_data(value).items():
                flat_data['{}__{}'.format(key, inner_key)] = inner_value

        elif type(value) is list and key == 'params':
            for param_dict in value:
                if type(param_dict) is not dict:
                    continue

                code = param_dict.get('typeid', {}).get('code')
                if code is None:
                    continue

                for inner_key, inner_value in flatten_object_data(param_dict).items():
                    flat_data['params__{}__{}'.format(code, inner_key)] = inner_value

        else:
            flat_data[key] = value

    return flat_data


def map_object_data(mapper_class, raw_object_data):
    """Выполняет маппинг сырых данных, полученных с сервера m3-rest-gar.

    Args:
        mapper_class: Класс-маппер.
        raw_object_data: Необработанные данные объекта ГАР, полученные с сервера m3-rest-gar.
    """

    flat_data = flatten_object_data(raw_object_data)
    mapped_data = mapper_class(flat_data)

    return mapped_data
