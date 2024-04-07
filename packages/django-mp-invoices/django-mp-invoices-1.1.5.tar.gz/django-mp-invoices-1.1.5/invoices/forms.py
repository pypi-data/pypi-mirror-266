
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from djforms.fields import DatePickerField
from exchange.constants import CURRENCIES
from customers.forms import CustomerChoiceField
from managers.forms import ManagerChoiceField
from suppliers.forms import SupplierChoiceField

from invoices.models import Sale


class ReportForm(forms.Form):

    date_from = DatePickerField(label=_('Date from'), required=False)

    date_to = DatePickerField(label=_('Date to'), required=False)

    is_profit_included = forms.BooleanField(
        label=_('Include profit'),
        initial=False,
        required=False)

    is_wholesale_price_included = forms.BooleanField(
        label=_('Include wholesale price'),
        initial=False,
        required=False)

    is_discount_included = forms.BooleanField(
        label=_('Include discount'),
        initial=False,
        required=False)

    manager = ManagerChoiceField()

    def __init__(self, data):

        today = datetime.now().date().strftime(settings.DATE_INPUT_FORMATS[0])

        super().__init__(
            data={
                'date_from': data.get('date_from', today),
                'date_to': data.get('date_to', today),
                'manager': data.get('manager'),
                'is_profit_included': data.get('is_profit_included'),
                'is_discount_included': data.get('is_discount_included'),
                'is_wholesale_price_included': data.get(
                    'is_wholesale_price_included')
            }
        )

        self.is_valid()


class ManageInvoiceForm(forms.Form):

    def __init__(self, invoice):

        self._invoice = invoice

        super().__init__(
            initial={
                'customer': invoice.customer,
                'manager': invoice.manager,
                'discount': invoice.discount,
                'currency': invoice.currency,
                'currency_rate': invoice.currency_rate,
            }
        )

        fields = self.fields

        fields['manager'] = self._create_contact_field(
            ManagerChoiceField, invoice.manager)

        fields['customer'] = self._create_contact_field(
            CustomerChoiceField, invoice.customer)

        if invoice.invoice_type == 'sale':
            fields['discount'] = forms.IntegerField(
                required=False,
                min_value=0)

            fields['discount'].widget.attrs = {
                'data-role': 'discount-input',
                'class': 'invoice-discount-input',
                'data-url': invoice.update_url,
                'min': 0
            }

            for field in Sale.TOTAL_FIELDS:
                fields[field] = forms.FloatField(
                    required=False,
                    initial=getattr(invoice, field)
                )
                fields[field].widget.attrs = {
                    'data-role': field.replace('service_', '').replace('_', '-'),
                    'class': 'total-input',
                    'data-url': invoice.update_url,
                    'min': 0
                }

        if invoice.invoice_type == 'arrival':
            fields['currency'] = forms.ChoiceField(
                choices=CURRENCIES, required=True)

            fields['supplier'] = self._create_contact_field(
                SupplierChoiceField, invoice.supplier)

            fields['currency_rate'] = forms.FloatField(
                required=False)

    def _create_contact_field(self, field_class, initial):
        field = field_class(initial=initial)
        field.widget.template_name = 'invoices/contact-select.html'
        field.widget.attrs = {'update_url': self._invoice.update_url}
        return field
