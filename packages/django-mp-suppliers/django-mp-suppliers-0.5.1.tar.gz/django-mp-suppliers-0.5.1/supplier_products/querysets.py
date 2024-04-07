
from django.db.models import Q

from model_search import model_search
from tecdoc.utils import clean_code
from exchange.querysets import MultiCurrencyQuerySet

from products.models import Product


class ProductQueryset(MultiCurrencyQuerySet):

    def search(
            self,
            code=None,
            description=None,
            manufacturer=None,
            **kwargs):

        is_empty = (
            code is None and
            description is None and
            manufacturer is None
        )

        if is_empty:
            return self.none()

        queryset = self

        if description:
            queryset = model_search(description, queryset, ['description'])

        if code:

            query = Q(clean_index=clean_code(code))

            products = Product.objects.search(
                code=code,
                description=description,
                manufacturer=manufacturer)

            for p in products:
                for cross in p.crosses.defer('src_value', 'dst_value'):
                    query |= Q(
                        clean_index=cross.clean_src_value,
                        manufacturer_id=cross.src_manufacturer_id)

                    query |= Q(
                        clean_index=cross.clean_dst_value,
                        manufacturer_id=cross.dst_manufacturer_id)

            queryset = queryset.filter(query)

        return queryset
