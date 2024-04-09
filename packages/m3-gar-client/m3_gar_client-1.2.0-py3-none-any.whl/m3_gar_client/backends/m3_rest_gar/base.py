from m3_gar_client.backends.base import (
    BackendBase as AbstractBackend,
)

from .utils import (
    find_address_objects,
    find_apartment,
    find_house,
    find_stead,
    get_address_object,
    get_apartment,
    get_house,
    get_stead,
)


class BackendBase(AbstractBackend):

    """Базовый бекенд для проксей к m3-rest-gar."""

    def find_address_objects(
        self,
        filter_string,
        levels=None,
        typenames=None,
        parent_id=None,
        timeout=None,
    ):
        """Возвращает адресные объекты, соответствующие параметрам поиска.

        Args:
            filter_string: Строка поиска
            levels: Уровни адресных объектов, среди которых нужно осуществлять поиск
            typenames: Наименования типов адресных объектов, среди которых нужно осуществлять поиск
            parent_id: ID родительского объекта
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Перечень адресных объектов.
        """

        return find_address_objects(filter_string, levels, typenames, parent_id, timeout)

    def get_address_object(self, obj_id, timeout=None):
        """Возвращает адресный объект ГАР по его ID.

        Args:
            obj_id: ID адресного объекта ГАР
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Адресный объект
        """

        return get_address_object(obj_id, timeout)

    def find_house(self, house_number, parent_id, building_number, structure_number, timeout=None):
        """Возвращает информацию о здании по его номеру.

        Args:
            house_number: Номер дома
            parent_id: ID родительского объекта
            building_number: Номер корпуса
            structure_number: Номер строения
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Найденные объекты зданий
        """

        return find_house(house_number, parent_id, building_number, structure_number, timeout)

    def get_house(self, house_id, timeout=None):  # pylint: disable=signature-differs
        """Возвращает информацию о здании по его ID в ГАР.

        Args:
            house_id: ID здания
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Найденный объект здания
        """

        return get_house(house_id, timeout)

    def find_stead(self, number, parent_id, timeout=None):
        """Возвращает информацию об участке по его номеру.

        Args:
            number: Номер участка
            parent_id: ID родительского объекта
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Найденные земельные участки
        """

        return find_stead(number, parent_id, timeout)

    def get_stead(self, stead_id, timeout=None):
        """Возвращает информацию о земельном участке по его ID в ГАР.

        Args:
            stead_id: ID земельного участка
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Найденный объект земельного участка
        """

        return get_stead(stead_id, timeout)

    def find_apartment(self, number, parent_id, timeout=None):
        """Возвращает информацию о помещении по его номеру.

        Args:
            number: Номер квартиры.
            parent_id: ID родительского объекта.
            timeout: Timeout запросов к серверу ГАР в секундах.
        """

        return find_apartment(number, parent_id, timeout)

    def get_apartment(self, apartment_id, timeout=None):
        """Возвращает информацию о помещении по его ID в ГАР.

        Args:
            apartment_id: ID помещения.
            timeout: Timeout запросов к серверу ГАР в секундах.

        Returns:
            Объект m3_gar_client.data.Apartment
        """

        return get_apartment(apartment_id, timeout)
