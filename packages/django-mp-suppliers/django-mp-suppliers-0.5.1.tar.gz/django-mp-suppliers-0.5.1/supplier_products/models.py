
import os

from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from suppliers.models import Supplier, SupplierWarehouse
from supplier_products.managers import ProductManager
from manufacturers.signals import manufacturer_replaced

from exchange.models import (
    MultiCurrencyPrice,
    subscribe_on_exchange_rates
)

from tecdoc.utils import clean_code


@subscribe_on_exchange_rates
class SupplierProduct(MultiCurrencyPrice):

    supplier = models.ForeignKey(
        Supplier,
        verbose_name=_('Supplier'),
        related_name='products',
        on_delete=models.CASCADE)

    warehouse = models.ForeignKey(
        SupplierWarehouse,
        verbose_name=_('Supplier warehouse'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    manufacturer = models.ForeignKey(
        'manufacturers.Manufacturer',
        verbose_name=_('Manufacturer'),
        related_name='supplier_products',
        on_delete=models.PROTECT,
        null=True,
        blank=True)

    index = models.CharField(_('Index'), max_length=255)

    clean_index = models.CharField(max_length=255, db_index=True)

    stock = models.CharField(_('Stock'), max_length=255)

    description = models.TextField(
        _('Description'), blank=True, max_length=2000)

    objects = ProductManager()

    def save(self, **kwargs):

        self.clean_index = clean_code(self.index)

        return super().save(**kwargs)

    def __str__(self):
        return self.index

    @property
    def printable_supplier(self):
        if self.warehouse_id:
            return '{} / {}'.format(self.supplier.code, self.warehouse.name)

        return self.supplier.code

    @property
    def search_link(self):

        query = self.index

        if self.manufacturer:
            query += ' ' + self.manufacturer.name

        return 'https://google.com/search?tbm=isch&q={}'.format(query)

    def serialize(self):
        return {
            'id': self.pk,
            'stock': self.stock,
            'price': self.price
        }

    @classmethod
    def replace_manufacturer(cls, sender, src_id, dst_id, **kwargs):
        cls.objects.filter(manufacturer=src_id).update(manufacturer_id=dst_id)

    class Meta:
        verbose_name = _('Supplier product')
        verbose_name_plural = _('Supplier products')


manufacturer_replaced.connect(SupplierProduct.replace_manufacturer)


class ImportTask(models.Model):

    created = models.DateTimeField(
        _('Creation date'),
        auto_now_add=True)

    file = models.FileField(
        _('File'),
        upload_to='import_cache',
        blank=True,
        null=True)

    is_completed = models.BooleanField(
        _('Is completed'),
        default=False)

    is_processing = models.BooleanField(_('Is processing'), default=False)

    status = models.CharField(_('Status'), max_length=255, blank=True)

    percent = models.CharField(_('Percent'), max_length=10, blank=True)

    supplier = models.ForeignKey(
        Supplier,
        verbose_name=_('Supplier'),
        on_delete=models.CASCADE)

    warehouse = models.ForeignKey(
        SupplierWarehouse,
        verbose_name=_('Supplier warehouse'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    should_data_be_cleaned = models.BooleanField(
        _('Clean previous prices'), default=False)

    def __str__(self):
        return str(self.created)

    def update_progress(
            self,
            percent,
            status=None,
            is_processing=None,
            is_completed=None):

        update_fields = ['percent']

        self.percent = percent

        if status is not None:
            self.status = status
            update_fields.append('status')

        if is_processing is not None:
            self.is_processing = is_processing
            update_fields.append('is_processing')

        if is_completed is not None:
            self.is_completed = is_completed
            update_fields.append('is_completed')

        self.save(update_fields=update_fields)

    @classmethod
    def get(cls, task_id):
        return cls.objects.get(id=task_id)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def get_status_url(self):
        return reverse_lazy('supplier-products:import-status', args=[self.pk])

    class Meta:
        ordering = ['-created']
        verbose_name = _('Import task')
        verbose_name_plural = _('Import tasks')
