
from django.contrib import admin
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from history.admin import LogHistoryAdmin
from product_barcode.filters import BarCodeFilter
from cap.actions import related_field_change_action
from cap.decorators import short_description, template_list_item
from tecdoc.filters import ProductCodeFilter
from exchange.utils import format_printable_price
from exchange.actions import update_prices
from categories.models import Category
from invoices.conf import IS_PRODUCT_PRICE_SHOWN_IN_DEFAULT_CURRENCY

from products.forms import ProductForm
from products.tasks import populate_product
from products.models import Product


@short_description(_('Stock report'))
def get_stock_report_action(modeladmin, request, queryset):
    url = reverse('stock:stock-report') + '?ids=' + ','.join(
        map(str, queryset.values_list('id', flat=True)))
    return redirect(url)


@short_description(_('Sync tecdoc'))
def sync_tecdoc_action(modeladmin, request, queryset):
    for product_id in queryset.values_list('id', flat=True):
        populate_product(product_id)


@admin.register(Product)
class ProductAdmin(LogHistoryAdmin):

    change_form_template = 'products/admin/changeform.html'

    history_group = 'products'

    form = ProductForm

    list_per_page = 250

    list_display = [
        'id', 'get_name_tag', 'warehouse', 'manufacturer', 'category',
        'printable_price', 'code', 'stock', 'is_active', 'tecdoc_cell',
        'get_item_actions'
    ]

    actions = [
        get_stock_report_action,
        update_prices,
        sync_tecdoc_action,
        related_field_change_action(
            Category,
            'category',
            _('Change category')
        )
    ]

    list_display_links = ['get_name_tag']

    list_filter = [
        BarCodeFilter,
        ProductCodeFilter,
        'category',
        'manufacturer'
    ]

    ordering = ['-id']

    search_fields = Product.search_fields

    autocomplete_fields = ['manufacturer']

    fields = (
        ('category', 'manufacturer', 'is_active', ),
        'name',
        ('code', 'bar_code', ),
        ('warehouse', 'unit_type', ),
        ('stock', 'min_stock', ),
        ('price_wholesale', 'price_retail', 'initial_currency', ),
        'additional_codes',
    )

    @short_description(
        _('Price, UAH')
        if IS_PRODUCT_PRICE_SHOWN_IN_DEFAULT_CURRENCY else
        _('Price')
    )
    def printable_price(self, item):
        return (
            item.price
            if IS_PRODUCT_PRICE_SHOWN_IN_DEFAULT_CURRENCY else
            format_printable_price(item.price_retail, item.initial_currency)
        )

    @template_list_item(
        'products/admin/list_item_actions.html', _('Actions'))
    def get_item_actions(self, item):
        return {'object': item}

    @template_list_item('products/admin/product_name.html', _('Name'))
    def get_name_tag(self, obj):
        return {'object': obj}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        populate_product(obj.pk)
        request.invoices.handle_product_change(obj)
