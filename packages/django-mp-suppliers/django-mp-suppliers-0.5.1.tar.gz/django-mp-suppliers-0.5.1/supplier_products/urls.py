
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

from supplier_products import views


app_name = 'supplier-products'


urlpatterns = [

    path('items/', views.get_products, name='items'),

    path('import/', views.start_import, name='start-import'),

    path('import/<int:task_id>/', views.process_import, name='process-import'),

    path('import/<int:task_id>/remove/', views.remove_import,
         name='remove-import'),

    path('import/<int:task_id>/status/', views.get_import_status,
         name='import-status'),

    path('create-product/<int:supplier_product_id>/', views.create_product,
         name='create-product'),

]


app_urls = i18n_patterns(
    path('supplier-products/', include((urlpatterns, app_name)))
)
