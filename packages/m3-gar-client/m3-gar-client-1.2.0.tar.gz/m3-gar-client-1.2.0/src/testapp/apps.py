from django.apps import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):

    name = __package__

    def _init_m3_gar_client(self):
        """Настраивает django-приложение m3_gar_client."""
        import m3_gar_client
        m3_gar_client.config = m3_gar_client.Config()

    def ready(self):
        self._init_m3_gar_client()

        super().ready()
