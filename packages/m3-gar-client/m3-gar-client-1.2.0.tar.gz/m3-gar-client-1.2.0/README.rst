Пакет ``m3-gar-client`` предоставляет панель для ввода адресов Российской Федерации с
использованием `ГАР <https://fias.nalog.ru/>`_ (Государственного адресного реестра),
готовую к использованию в проектах на базе платформы
`M3 <http://m3.bars-open.ru/>`_ компании `БАРС Груп <http://bars.group>`_.

Возможности
-----------

* Работа с сервером ГАР `m3-rest-gar <https://stash.bars-open.ru/projects/M3/repos/m3-rest-gar>`_.
* Встраивание в интерфейс веб-приложений на базе ExtJS.
* Поиск адресов в ГАР по мере ввода наименований адресных объектов (субъектов
  Федерации, населенных пунктов, улиц, зданий).

Системные требования
--------------------

* `Python <http://www.python.org/>`_ 3.6+
* `Django <http://djangoproject.com/>`_ 2.2 - 4.0
* `m3-core <https://pypi.python.org/pypi/m3-core>`_ 2.2
* `m3-ui <https://pypi.python.org/pypi/m3-ui>`_ 2.2


Подключение в варианте M3
-------------------------

Установка:

.. code-block:: bash

  $ pip install m3-gar-client[m3]


Настройка:

.. code-block:: python

  INSTALLED_APPS += [
      'testapp',
      'rest_framework',
      'm3_gar_client',
  ]

  GAR_API_URL = 'http://gar.bars.group/gar/v1/'

  GAR = dict(
      BACKEND='m3_gar_client.backends.m3_rest_gar.proxy',  # <---
      URL=GAR_API_URL,
      USE_CACHE=True,
      USE_SIMPLE_SERVER=True,
  )


Подключение в варианте REST
---------------------------

Установка:

.. code-block:: bash

  $ pip install m3-gar-client[rest]


Настройка:

.. code-block:: python

  INSTALLED_APPS += [
      'testapp',
      'rest_framework',
      'm3_gar_client',
  ]

  GAR_API_URL = 'http://gar.bars.group/gar/v1/'

  GAR = dict(
      BACKEND='m3_gar_client.backends.m3_rest_gar.proxy_rest',  # <---
      URL=GAR_API_URL,
      USE_CACHE=True,
      USE_SIMPLE_SERVER=True,
      REST=dict(
          AUTHENTICATION_CLASSES=[
              'oidc_auth.authentication.JSONWebTokenAuthentication'
          ],
          PERMISSION_CLASSES=[
              'rest_framework.permissions.IsAuthenticated'
          ]
      )
  )


Настройки
---------
- ``URL`` --- URL API сервера ГАР.
- ``TIMEOUT`` --- timeout запроса к серверу ГАР в секундах.
- ``PAGE_LIMIT`` --- количество страниц запрашиваемых у m3-rest-gar, по умолчанию 1. При большом количестве можно заддосить ГАР
- ``USE_CACHE`` --- определяет необходимость кеширования HTTP-запросов
  к серверу m3-rest-gar. Значение по умолчанию: ``False``
- ``CACHE_TIMEOUT`` --- определяет длительность кэширования (в секундах). Значение по умолчанию: 24 часа
- ``USE_SIMPLE_SERVER`` --- Использовать простой сервер, по умолчанию будет использоваться сервер OAUTH2
- ``OAUTH2`` --- параметры OAuth2: необходиы если не указано использовать простой сервер

  - ``TOKEN_URL`` --- URL для получения токена, должен использоваться HTTPS.
  - ``CLIENT_ID`` --- id клиента - создается на стороне РЕСТ сервера
  - ``CLIENT_SECRET`` --- Секретный ключ клиента - генерируется на стороне РЕСТ сервера
  - ``USERNAME`` --- username пользователя для получения токена
  - ``PASSWORD`` --- password пользователя для получения токена

