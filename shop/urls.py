from django.urls import path
from shop import views

app_name = 'shop'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),

    path('catalog/', views.ModelsListView.as_view(), name='products'),
    path('catalog/search/', views.heandler_search,
         name='search_heandler'),
    path('catalog/search/<str:search_line>/',
         views.SearchListView.as_view(), name='search'),

    path('catalog/<slug:ct_model>/',
         views.ModelListView.as_view(), name='models_view'),
#     path('catalog/category/<slug:category>/', name='categories'),
    path('catalog/<str:ct_model>/<slug:slug>/',
         views.ProductDetailView.as_view(), name='product_page'),
    path('catalog/<str:ct_model>/<str:category>/',
         views.ModelsCategoryListView.as_view(), name='category_model_view'),


    # path('products/<slug:ct_model>/<str:category_slug>', some_view, name='category_model')
]
