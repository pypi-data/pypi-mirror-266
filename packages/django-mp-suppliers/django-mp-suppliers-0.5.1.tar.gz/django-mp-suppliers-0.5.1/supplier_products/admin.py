
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from cap.decorators import template_list_item

from supplier_products.models import SupplierProduct, ImportTask


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):

    list_per_page = 50
    search_fields = ['description', 'index']
    list_filter = ['supplier']
    list_display = [
        'id',
        'supplier',
        'manufacturer',
        'index',
        'description',
        'price',
        'stock',
        'get_item_actions'
    ]
    fields = (
        ('supplier', 'warehouse', ),
        ('manufacturer', 'index'),
        'description',
        ('price_retail', 'stock', ),
    )
    change_list_template = 'supplier_products/admin/list.html'
    list_select_related = ['supplier', 'warehouse', 'manufacturer']

    @template_list_item(
        'supplier_products/admin/list_item_actions.html', _('Actions'))
    def get_item_actions(self, item):
        return {'object': item}

    def changelist_view(self, request, extra_context=None):

        context = extra_context or {}

        context['unprocessed_files'] = ImportTask.objects.filter(
            is_completed=False, is_processing=False)

        context['processing_files'] = ImportTask.objects.filter(
            is_completed=False, is_processing=True)

        return super().changelist_view(request, extra_context=context)


@admin.register(ImportTask)
class ImportTaskAdmin(admin.ModelAdmin):

    list_display = [
        'id', 'supplier', 'should_data_be_cleaned', 'created', 'status',
        'percent', 'is_processing', 'is_completed'
    ]
