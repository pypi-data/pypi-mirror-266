from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from cap.decorators import short_description


@short_description(_('Print'))
def print_action(modeladmin, request, queryset):
    return render(request, "invoices/print-multiple.html", {
        "queryset": queryset
    })
