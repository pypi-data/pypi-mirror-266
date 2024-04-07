
import logging

from django.urls import reverse_lazy, reverse
from django.http.response import (
    JsonResponse,
    HttpResponse,
    HttpResponseBadRequest
)
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from sxl import Workbook
from categories.models import Category

from supplier_products.models import SupplierProduct, ImportTask
from supplier_products.forms import ImportTaskForm, ProcessImportForm
from supplier_products.tasks import import_supplier_products

from products.forms import SearchProductForm

from products.models import Product


logger = logging.getLogger(__name__)


@staff_member_required
def start_import(request):

    form = ImportTaskForm(request.POST or None, request.FILES or None)

    status_code = 200

    if request.method == 'POST':

        if form.is_valid():

            task = form.save()

            return JsonResponse({
                'url': reverse_lazy(
                    'supplier-products:process-import', args=[task.pk])
            })
        else:
            status_code = 403

    return render(
        request,
        'supplier_products/start_import.html',
        {'form': form, 'status_code': status_code},
        status=status_code)


@staff_member_required
def process_import(request, task_id):

    form = ProcessImportForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        import_supplier_products.delay(task_id, form.cleaned_data)

        messages.success(request, _('File added to process group'))

        return redirect('admin:supplier_products_supplierproduct_changelist')

    task = get_object_or_404(ImportTask, pk=task_id, is_completed=False)

    try:
        worksheet = Workbook(task.file.path).sheets
        worksheet = worksheet[1]
    except Exception as e:
        messages.error(request, e)
        return redirect('admin:supplier_products_supplierproduct_changelist')

    return render(request, 'supplier_products/process_import.html', {
        'form': form,
        'task': task,
        'rows': list(worksheet.head())
    })


@require_POST
@staff_member_required
def remove_import(request, task_id):
    ImportTask.objects.filter(pk=task_id).delete()
    return redirect('admin:supplier_products_supplierproduct_changelist')


@staff_member_required
def get_import_status(request, task_id):

    task = get_object_or_404(ImportTask, pk=task_id)

    return JsonResponse({
        'percent': task.percent,
        'text': '{}% ({})'.format(task.percent, task.status)
    })


@login_required
def get_products(request):

    form = SearchProductForm(data=request.GET)

    if not form.is_valid():
        return HttpResponseBadRequest('Invalid form')

    supplier_products = []

    if request.user.is_staff:
         supplier_products = SupplierProduct.objects.search(
             **form.cleaned_data
         ).select_related(
             'manufacturer',
             'supplier',
             'warehouse'
         ).only(
             'manufacturer__name',
             'warehouse__name',
             'supplier__code',
             'index',
             'description',
             'stock',
             'price_uah',
             'price_eur',
             'price_usd'
         ).set_currency(request)

    html = ''

    for obj in supplier_products:
        html += render_to_string('supplier_products/list_item.html', {
            'object': obj,
            'is_staff': request.user.is_staff
        })

    return HttpResponse(html)


@csrf_exempt
@require_POST
@staff_member_required
def create_product(request, supplier_product_id):

    src_product = get_object_or_404(SupplierProduct, pk=supplier_product_id)

    if Product.objects.filter(code=src_product.index).exists():
        return HttpResponseBadRequest(
            _('Product with this code already exists: {}').format(
                src_product.index)
        )

    category = get_object_or_404(Category, name='SUPPLIERS')

    dst_product = Product.objects.create(
        category=category,
        manufacturer=src_product.manufacturer,
        name=src_product.description,
        code=src_product.index,
        **src_product.price_values
    )

    src_product.delete()

    return HttpResponse(
        reverse('admin:products_product_change', args=[dst_product.id]))
