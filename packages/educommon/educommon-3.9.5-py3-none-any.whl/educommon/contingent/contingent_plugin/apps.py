from importlib import (
    import_module,
)

from django import (
    VERSION,
)
from django.apps.config import (
    AppConfig,
)


_VERSION = VERSION[:2]


class ContingentPluginAppConfig(AppConfig):

    name = __package__

    if _VERSION >= (3, 2):
        default = False

    def _register_related_objects_views(self):
        """Добавляет представления для моделей приложения."""
        from educommon.django.db.model_view import (
            registries,
        )

        model_views = import_module(self.name + '.model_views')
        registries['related_objects'].register(
            *model_views.related_model_views
        )

    def ready(self):
        super(ContingentPluginAppConfig, self).ready()
        self._register_related_objects_views()
