
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from product_barcode.utils import validate_barcode
from djforms.fields import DatePickerField
from categories.models import Category

from products.models import Product


class ProductForm(forms.ModelForm):

    def clean_bar_code(self):

        bar_code = self.cleaned_data.get('bar_code')

        if bar_code:
            validate_barcode(bar_code, self.instance.pk)

        return bar_code

    def clean(self):

        data = self.cleaned_data

        if not data.get('price_wholesale') or not data.get('price_retail'):
            return data

        if data['price_wholesale'] > data['price_retail']:
            raise ValidationError(
                _('Wholesale price can`t be greater than retail price'))

        return data

    class Meta:
        model = Product
        fields = '__all__'


class SearchProductForm(forms.Form):

    code = forms.CharField(required=False)

    bar_code = forms.CharField(required=False)

    query = forms.CharField(required=False)

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.HiddenInput)

    def clean(self):

        cleaned_data = {}

        for k, v in self.cleaned_data.items():
            if v:
                cleaned_data[k] = v

        return cleaned_data


class HistoryForm(forms.Form):

    date_from = DatePickerField(label=_('Date from'))

    date_to = DatePickerField(label=_('Date to'))

    def __init__(self, data):

        today = datetime.now().date().strftime(settings.DATE_INPUT_FORMATS[0])

        super().__init__(
            data={
                'date_from': data.get('date_from', today),
                'date_to': data.get('date_to', today)
            }
        )
