from django.conf import (
    settings,
)
from django.test.testcases import (
    TestCase,
)
from rest_framework.permissions import (
    IsAuthenticated,
)

from m3_gar_client.backends.m3_rest_gar.proxy_rest.authentication import (
    CsrfExemptSessionAuthentication,
)
from m3_gar_client.backends.m3_rest_gar.proxy_rest.views import (
    get_authentication_classes,
    get_permission_classes,
)


class DefaultsTestCase(TestCase):

    """Проверка конфигурации по-умолчанию.

    Конфигурация соответствует поведению монолитных продуктов.
    """

    def test_defaults(self):
        # Конфиг не задан
        self.assertIsNone(settings.GAR.get('REST'))

        self.assertEqual(
            get_authentication_classes(),
            [CsrfExemptSessionAuthentication]
        )

        self.assertEqual(
            get_permission_classes(),
            [IsAuthenticated]
        )
