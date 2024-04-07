
from django.utils.translation import gettext_lazy as _

from product_barcode.models import BarCode
from tecdoc import utils

from products.models import Product


class PopulateError(Exception):
    pass


def populate_product(product_id):

    message = ''

    product = Product.objects.select_related('manufacturer').get(pk=product_id)

    try:
        _populate_from_tecdoc(product)
    except Exception as e:
        message = str(e)

    print('Message: ', message)

    if not product.bar_code:
        product.bar_code = BarCode.get_solo().get_next_code()

    product.save()

    return {
        'message': message
    }


def _populate_from_tecdoc(product):

    if not product.manufacturer:
        raise PopulateError(_('Manufacturer not set'))

    if not product.code:
        raise PopulateError(_('Product code not set'))

    supplier = utils.get_supplier(
        product.manufacturer.new_name or product.manufacturer.name)

    if not supplier:
        raise PopulateError(_('Supplier not found'))

    print('Supplier: ', supplier.id)

    article = utils.get_article(supplier, product.clean_code)

    if not article and product.bar_code:
        article = utils.get_article_by_ean(supplier, product.bar_code)

    if not article:
        raise PopulateError(_('Article not found'))

    product.article_number = article.article_number
    product.supplier_id = article.supplier_id

    if not product.bar_code:
        ean = utils.get_article_ean(supplier, article.article_number)
        if ean:
            product.bar_code = ean.ean

    product.additional_codes = utils.clean_additional_codes(
        supplier, article.article_number, product.additional_codes)
