from django.urls import path
from django.views.generic.base import View
from . import views

app_name = 'orders'


# in the beginning need user pk!
urlpatterns = [
    path('', views.CartListView.as_view(), name='detail_cart'),
    path('add-to-cart/<str:model_name>/<slug:slug>/',
         views.AddToCartView.as_view(), name='add_to_cart'),
    path('delete-product/<str:model_name>/<slug:slug>/',
         views.DeleteProduct.as_view(), name='delete_product'),
    path('save-product/<str:model_name>/<slug:slug>/',
         views.SaveValuesChanges.as_view(), name='save_product'),
    path('create-order/', views.CreateOrderView.as_view(), name='create_order'),
    path('orders/<slug:id>/', view=views.OrderDetailView.as_view(), name='detail_order')
]
