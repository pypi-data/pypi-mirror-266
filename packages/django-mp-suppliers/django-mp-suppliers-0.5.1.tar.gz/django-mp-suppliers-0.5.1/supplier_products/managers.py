
from exchange.managers import MultiCurrencyManager

from supplier_products.querysets import ProductQueryset


class ProductManager(MultiCurrencyManager):

    def get_queryset(self):
        return ProductQueryset(self.model, using=self._db)

    def search(self, **kwargs):
        return self.get_queryset().search(**kwargs)
