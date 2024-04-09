from django.contrib.auth.models import (
    User,
)
from django.test import (
    Client,
)
from django.test.testcases import (
    TestCase,
)

from m3_gar_client.backends.m3_rest_gar.proxy_rest import (
    Backend,
)


class BackendsResultsTestCase(TestCase):

    def test_backends_results(self):
        backend = Backend()

        client = Client()
        user, _ = User.objects.get_or_create(username='testuser')
        client.force_login(user)  # Запросы требуют авторизации

        # Проверка получения нас. пункта
        place_url = backend.place_search_url
        self.assertIsInstance(place_url, str)
        self.assertGreater(len(place_url), 0)

        response = client.post(place_url, {'filter': 'ujhjl Yjdjcb,bhcr'})
        self.assertGreater(response.json()['total'], 0)

        place = response.json()['rows'][1]

        # Проверка получения улицы в нас. пункте
        street_url = backend.street_search_url
        self.assertIsInstance(street_url, str)
        self.assertGreater(len(street_url), 0)

        response = client.post(street_url, {'filter': 'Ktybyf', 'parent': place['objectId']})
        self.assertGreater(response.json()['total'], 0)

        street = response.json()['rows'][1]

        # Проверка получения дома на улице
        house_url = backend.house_search_url
        self.assertIsInstance(house_url, str)
        self.assertGreater(len(house_url), 0)

        response = client.post(house_url, {'filter': '18', 'parent': street['objectId']})
        self.assertGreater(response.json()['total'], 0)
        house = response.json()['rows'][0]

        # проверка получения квартиры в доме
        apartment_url = backend.apartment_search_url
        self.assertIsInstance(apartment_url, str)
        self.assertGreater(len(apartment_url), 0)

        response = client.post(apartment_url, {'filter': '84', 'parent': house['objectId']})
        self.assertGreater(response.json()['total'], 0)
