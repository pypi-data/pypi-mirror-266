
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from cap.decorators import template_list_item, short_description
from rangefilter.filters import DateRangeFilter

from invoices.actions import print_action
from invoices.conf import ARE_SALE_TOTALS_VISIBLE
from invoices.models import Arrival, Sale


class InvoiceAdmin(admin.ModelAdmin):

    actions = [print_action]
    list_per_page = 100

    def has_add_permission(self, request):
        return False

    @template_list_item('invoices/name_cell.html', _('Created'))
    def get_name(self, obj):
        return {'object': obj}

    get_name.admin_order_field = 'created'

    @short_description(_('Total'))
    def get_total(self, obj):
        if isinstance(obj, Sale):
            return obj.total_with_discount + obj.service_total
        return '{} {}'.format(obj.total, obj.get_currency_display())

    @short_description(_('Total qty'))
    def get_total_qty(self, obj):
        return obj.total_qty

    @template_list_item('invoices/list_item_actions.html', _('Actions'))
    def get_item_actions(self, obj):
        return {'object': obj}

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            queryset |= self.model.objects.filter(
                customer__phone__icontains=(
                    search_term
                    .replace("-", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace(" ", "")
                )
            )
        return queryset, use_distinct


@admin.register(Sale)
class SaleAdmin(InvoiceAdmin):

    list_display = [
        'get_name',
        'type',
        'customer',
        'creator',
        'get_total_qty'
    ] + (
        [
            "get_total_cassa",
            "get_total_card",
            "get_total_post",
        ] if ARE_SALE_TOTALS_VISIBLE else []
    ) + [
        'get_total',
        'get_item_actions'
    ]
    list_display_links = ['type']
    list_filter = [
        'type',
        ('created', DateRangeFilter),
        'creator',
        'customer'
    ]
    search_fields = ['id', 'customer__name', 'customer__phone']

    @short_description(_('Cassa'))
    def get_total_cassa(self, obj):
        return '%s / %s' % (obj.total_cassa, obj.service_total_cassa)

    @short_description(_('Credit card'))
    def get_total_card(self, obj):
        return '%s / %s' % (obj.total_card, obj.service_total_card)

    @short_description(_('Nova poshta'))
    def get_total_post(self, obj):
        return '%s / %s' % (obj.total_post, obj.service_total_post)


@admin.register(Arrival)
class ArrivalAdmin(InvoiceAdmin):

    list_display = [
        'get_name',
        'type',
        'customer',
        'supplier',
        'creator',
        'get_total_qty',
        'get_total',
        'get_item_actions'
    ]
    list_display_links = ['type']
    list_filter = ['type', 'creator', 'created', 'supplier']
    search_fields = [
        'id',
        'supplier__name',
        'supplier__short_name',
        'customer__name',
        'customer__phone'
    ]
