
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.contrib.admin.views.decorators import staff_member_required

from pagination import paginate

from cap.decorators import admin_render_view

from djforms import get_clean_data
from products import forms

from products.models import Product


def get_id_from_bar_code(request):
    product = get_object_or_404(Product, bar_code=request.GET.get('bar_code'))
    return HttpResponse(product.id)


@admin_render_view(template_name='products/print_name.html')
def print_product_name(request, product_id):
    return {'product': get_object_or_404(Product, pk=product_id)}


@admin_render_view(template_name='products/print_bar_code.html')
def print_product_bar_code(request, product_id):
    return {'product': get_object_or_404(Product, pk=product_id)}


@admin_render_view(template_name='products/history.html')
def get_product_history(request, product_id):

    product = get_object_or_404(Product, pk=product_id)

    form = forms.HistoryForm(request.GET)

    data = get_clean_data(form)

    date_from = data['date_from']
    date_to = data['date_to']

    sale_items = (
        product
        .saleitem_set
        .filter(invoice__created__date__range=[date_from, date_to])
        .select_related('invoice')
        .order_by('-invoice__created')
    )

    arrival_items = (
        product
        .arrivalitem_set
        .filter(invoice__created__date__range=[date_from, date_to])
        .select_related('invoice')
        .order_by('-invoice__created')
    )

    all_items = list(
        product
        .saleitem_set
        .select_related('invoice')
        .all()
    )

    all_items += list(
        product
        .arrivalitem_set
        .select_related('invoice')
        .all()
    )

    all_items.sort(key=lambda r: r.invoice.created, reverse=True)

    return {
        'product': product,
        'form': form,
        'sale_items': sale_items,
        'sale_totals': {
            'total': sum([s.subtotal_with_discount for s in sale_items]),
            'qty': sum([s.qty for s in sale_items])
        },
        'arrival_items': arrival_items,
        'arrival_totals': {
            'total': sum([s.subtotal_with_discount for s in arrival_items]),
            'qty': sum([s.qty for s in arrival_items])
        },
        'all_items': all_items
    }


@require_GET
@staff_member_required
def get_products(request):

    form = forms.SearchProductForm(request.GET)

    page = paginate(
        request,
        Product.objects.active().search(**get_clean_data(form)),
        per_page=20)

    return JsonResponse({
        'items': render_to_string('invoices/product-items.html', {
            'request': request,
            'page_obj': page
        }),
        **page.serialize()
    })
