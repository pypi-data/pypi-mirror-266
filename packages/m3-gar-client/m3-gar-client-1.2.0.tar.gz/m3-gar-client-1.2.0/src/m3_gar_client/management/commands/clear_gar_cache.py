from django.core.cache import (
    cache,
)
from django.core.management import (
    BaseCommand,
)

from m3_gar_client.backends.m3_rest_gar.server import (
    server,
)


class Command(BaseCommand):
    """Команда очищает все ключи кеша ГАР"""

    def handle(self, *args, **options):
        cache.delete_many(keys=cache.keys(f'{server.cache_key_prefix}*'))
        self.stdout.write('Очистка завершена')
