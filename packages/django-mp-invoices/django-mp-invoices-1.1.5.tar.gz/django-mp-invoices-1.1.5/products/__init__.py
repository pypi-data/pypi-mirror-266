
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


def setup_settings(settings, is_prod, **kwargs):

    settings['INSTALLED_APPS'] += [
        app for app in [
            'djforms',
            'pagination'
        ] if app not in settings['INSTALLED_APPS']
    ]


class ProductsAppConfig(AppConfig):

    name = 'products'
    verbose_name = _('Products')


default_app_config = 'products.ProductsAppConfig'
