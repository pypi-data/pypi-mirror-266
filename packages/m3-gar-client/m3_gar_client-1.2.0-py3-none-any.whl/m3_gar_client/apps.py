import warnings

from django.apps.config import (
    AppConfig as AppConfigBase,
)

import m3_gar_client


class AppConfig(AppConfigBase):

    name = __package__

    def ready(self):
        super().ready()

        if m3_gar_client.config:
            m3_gar_client.config.backend.init()
        else:
            warnings.warn("Не указана конфигурация m3-gar, пакет не будет инициализирован")
