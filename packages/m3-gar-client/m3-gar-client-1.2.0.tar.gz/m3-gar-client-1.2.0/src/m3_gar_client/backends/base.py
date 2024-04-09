from abc import (
    ABC,
    abstractmethod,
)


class BackendBase(ABC):

    """Базовый класс для бэкендов."""

    def init(self):
        """Метод инициализации бекенда и бутстреппинга пакета."""

    @property
    @abstractmethod
    def place_search_url(self):
        """URL для поиска населенных пунктов.

        :rtype: str
        """

    @property
    @abstractmethod
    def street_search_url(self):
        """URL для поиска улиц.

        :rtype: str
        """

    @property
    @abstractmethod
    def house_search_url(self):
        """URL для запроса списка домов.

        :rtype: str
        """

    def configure_place_field(self, field):
        """Настраивает поле "Населенный пункт".

        :param field: Поле "Населенный пункт".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    def configure_street_field(self, field):
        """Настраивает поле "Улица".

        :param field: Поле "Улица".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    def configure_house_field(self, field):
        """Настраивает поле "Дом".

        :param field: Поле "Дом".
        :type field: m3_ext.ui.fields.simple.ExtComboBox
        """

    @abstractmethod
    def find_address_objects(
        self,
        filter_string,
        levels=None,
        typenames=None,
        parent_id=None,
        timeout=None,
    ):
        """Возвращает адресные объекты, соответствующие параметрам поиска.

        :param str filter_string: Строка поиска.
        :param levels: Уровни адресных объектов, среди которых нужно осуществлять поиск.
        :param parent_id: ID родительского объекта.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: generator
        """

    @abstractmethod
    def get_address_object(self, obj_id, timeout=None):
        """Возвращает адресный объект ГАР по его ID.

        :param obj_id: ID адресного объекта ГАР.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.AddressObject
        """

    @abstractmethod
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

    @abstractmethod
    def get_house(self, house_id, timeout=None):
        """Возвращает информацию о здании по его ID в ГАР.

        :param house_id: ID здания.
        :param float timeout: Timeout запросов к серверу ГАР в секундах.

        :rtype: m3_gar_client.data.House
        """

    @abstractmethod
    def find_stead(self, number, parent_id, timeout=None):
        """Возвращает информацию об участке по его номеру.

        Args:
            number: Номер участка
            parent_id: ID родительского объекта
            timeout: Timeout запросов к серверу ГАР в секундах

        Returns:
            Найденные земельные участки
        """

    @abstractmethod
    def get_stead(self, stead_id, timeout=None):
        """Возвращает информацию о земельном участке по его ID в ГАР.

        Args:
            stead_id: ID земельного участка.
            timeout: Timeout запросов к серверу ГАР в секундах.

        Returns:
            Объект m3_gar_client.data.House
        """

    @abstractmethod
    def find_apartment(self, number, parent_id, timeout=None):
        """Возвращает информацию о помещении по его номеру.

        Args:
            number: Номер квартиры.
            parent_id: ID родительского объекта.
            timeout: Timeout запросов к серверу ГАР в секундах.
        """

    @abstractmethod
    def get_apartment(self, apartment_id, timeout=None):
        """Возвращает информацию о помещении по его ID в ГАР.

        Args:
            apartment_id: ID помещения.
            timeout: Timeout запросов к серверу ГАР в секундах.

        Returns:
            Объект m3_gar_client.data.Apartment
        """
