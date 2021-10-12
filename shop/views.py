from re import split, template
import re
from typing import List
from django.contrib.auth.models import User
from django.contrib.messages.api import warning
from django.db.models import query
from django.db.models.query_utils import Q
from django.forms import boundfield
from django.http.response import ResponseHeaders
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls.base import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.http import Http404, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .const import CT_MODEL_CLASS, get_product_models
from .models import *
from .forms import *
from shop import const, urls
from itertools import chain, groupby
from accounts.views import LoginFormView
from orders.orders_services import Orders_service
from orders.models import Cart, CartProduct


def index(request):
    return HttpResponse('<h1>Hello world</h1>')


class HomePageView(ListView):
    template_name = 'shop/home.html'
    model = ContentType

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = [list(i.objects.order_by('-pub_date'))
                    for i in const.get_product_models().values()]

        queryset = sorted(chain(*queryset),
                          key=lambda instance: instance.pub_date, reverse=True)

        context['new_products'] = queryset[:5]

        return context

    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)


class ProductDetailView(DetailView, Orders_service):

    template_name = 'shop/product_page.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    success_url = None
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.model = get_product_models()[kwargs['ct_model']]
        self.success_url = request.path
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = kwargs['object'].comments.all().order_by(
            '-pub_date')
        context['form'] = CommentForm()
        context['product_model'] = context['product']._meta.model_name
        context['success_url'] = self.success_url
        context['is_in_cart'] = False

        if self.user.is_authenticated:

            result = self.is_product_added(
                context['product_model'],  context['product'].slug, self.user.account.cart)

            if result == None:
                context['add_btn_text'] = 'В корзину'
            else:
                context['add_btn_text'] = 'В корзине: ' + str(result.quantity)
                context['is_in_cart'] = True

        else:
            context['add_btn_text'] = 'В корзину'

        return context

    def post(self, request, *args, **kwargs):
        bound_form = CommentForm(request.POST)

        if request.user.is_authenticated:
            bound_form.full_clean()

            if bound_form.is_valid():
                model = get_product_models()[kwargs['ct_model']]
                product = model.objects.get(slug=kwargs['slug'])
                new_comment = bound_form.save(
                    content_object=product, user=request.user)
                return HttpResponseRedirect(reverse('shop:product_page', kwargs=kwargs))

            else:

                return render(request, self.template_name, context={'form': bound_form})
        else:

            print('\n\n\n\n\n\n', bound_form.errors)
            messages.warning(
                request, 'Авторизируйтесь чтобы оставить комментарий')
            return redirect(reverse('accounts:login'))


class ModelListView(ListView):

    template_name = 'shop/list_page2.html'

    def dispatch(self, request, *args, **kwargs):
        content_type = ContentType.objects.get(model=kwargs['ct_model'])
        self.model = content_type.model_class()
        self.ct_model = kwargs['ct_model']
        self.queryset = self.model.objects.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.ct_model
        context['model'] = self.model
        context['model_name'] = self.model._meta.verbose_name
        context['categories'] = self.model.objects.get_categories_for_model().keys()

        return context


class ModelsCategoryListView(ModelListView):
    model = None
    template_name = 'shop/list_page2.html'

    def dispatch(self, request, *args, **kwargs):
        super(ModelsCategoryListView, self).dispatch(request, *args, **kwargs)

        self.queryset = self.queryset.filter(
            categories__name__in=[kwargs['category']])

        return View.dispatch(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.kwargs['category']
        return context


class ModelsListView(ListView):

    template_name = 'shop/list_page.html'
    model = GenericCategory
    _models_category = {}
    _models_class = {}

    def get_context_data(self, **kwargs):
        for key, value in get_product_models().items():
            self.name = value._meta.verbose_name_plural
            self._models_category[self.name] = {
                'ct_model': value,
                'category_set': value.objects.get_categories_for_model(),
                'model_set': value.objects.all()
            }

        context = super().get_context_data(**kwargs)
        context['categoryset'] = self._models_category
        print(context)

        return context


class LeaveCommentView(View):

    def post(self, request, *args, **kwargs):
        bound_form = CommentForm(request.POST)

        if bound_form.is_valid():
            model = get_product_models()[kwargs['ct_model']]
            product = model.objects.get(slug=kwargs['slug'])
            new_comment = bound_form.save(content_object=product)

        return HttpResponseRedirect(reverse('shop:product_page', kwargs=kwargs))


def heandler_search(request):
    if request.method == 'POST':
        line = '-'.join(request.POST['search_line'].split())
        if line:
            return HttpResponseRedirect(reverse('shop:search', kwargs={'search_line': line}))
        return HttpResponseRedirect(request.GET.get('next'))


class SearchListView(ListView):
    template_name = 'shop/search_responce.html'
    paginate_by = 2

    def dispatch(self, request, *args, **kwargs):
        search_list = kwargs['search_line'].split('-')
        responce_list = []

        for model in get_product_models().values():
            _list = []
            for parametr in search_list:
                queryset = model.objects.filter(
                    Q(name__icontains=parametr) | Q(name__istartswith=parametr)
                )

                if queryset:
                    _list.extend(list(queryset))

            _list = [product for product, _ in groupby(_list)]
            responce_list.extend(_list)

        self.queryset = responce_list

        if not self.queryset:
            self.paginate_by = None
            messages.info(
                request, f'По запроссу \'{" ".join(search_list)}\' ничего не найдено :(')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.paginate_by:
            context['range_page_obj'] = range(
                1, context['page_obj'].paginator.num_pages+1)
        return context
