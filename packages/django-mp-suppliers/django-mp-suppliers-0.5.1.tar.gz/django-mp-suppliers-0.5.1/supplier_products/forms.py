
from django import forms
from django.utils.translation import gettext_lazy as _

from supplier_products.models import ImportTask


class ImportTaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True
        self.fields['file'].label = _('File') + ', XLSX'

    def clean(self):
        data = self.cleaned_data

        supplier = data.get('supplier')
        warehouse = data.get('warehouse')

        if supplier and warehouse and supplier.id != warehouse.supplier_id:
            raise forms.ValidationError('Incorrect warehouse')

        return data

    class Meta:
        model = ImportTask
        fields = ['should_data_be_cleaned', 'file', 'supplier', 'warehouse']


class ProcessImportForm(forms.Form):

    manufacturer = forms.IntegerField(required=False)
    index = forms.IntegerField()
    price = forms.IntegerField()
    stock = forms.IntegerField()
    description = forms.IntegerField(required=False)
