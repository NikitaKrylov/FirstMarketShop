import re
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Account
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls.base import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from shop.const import CT_MODEL_CLASS, get_product_models
from django.views import View
from django.views.generic.edit import CreateView, FormView
from django.views.generic import ListView
from .models import Cart, CartProduct
from accounts.models import Order
from .orders_services import Orders_service
from .forms import CreateOrderForm
from accounts.mixins import AccountMixin


class AddToCartView(LoginRequiredMixin, View, Orders_service):
    redirect_to = None
    login_url = reverse_lazy('shop:home')

    def dispatch(self, request, *args, **kwargs):
        model_name, product_slug = kwargs.get('model_name'), kwargs.get('slug')
        user_cart = request.user.account.get_or_create_cart()

        self.add_new_product(model_name, product_slug, user_cart)

        self.redirect_to = request.META.get('HTTP_REFERER')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.redirect_to)


class DeleteProduct(LoginRequiredMixin, View, Orders_service):
    redirect_to = None
    login_url = reverse_lazy('shop:home')

    def dispatch(self, request, *args, **kwargs):
        model_name, product_slug = kwargs.get('model_name'), kwargs.get('slug')
        user_cart = request.user.account.get_or_create_cart()

        self.delete_product(model_name, product_slug, user_cart)

        self.redirect_to = request.META.get('HTTP_REFERER')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.redirect_to)


class SaveValuesChanges(LoginRequiredMixin, View, Orders_service):
    redirect_to = None
    login_url = reverse_lazy('shop:home')

    def dispatch(self, request, *args, **kwargs):
        self.redirect_to = request.META.get('HTTP_REFERER')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        model_name, product_slug = kwargs.get('model_name'), kwargs.get('slug')
        user_cart = request.user.account.get_or_create_cart()

        self.update_product_quantity(
            model_name, product_slug, user_cart, request.POST['quantity'])

        return HttpResponseRedirect(self.redirect_to)


class CartListView(LoginRequiredMixin, ListView):
    template_name = 'orders/main_cart.html'
    model = Cart
    login_url = reverse_lazy('shop:home')

    def dispatch(self, request, *args, **kwargs):
        self.queryset = self.model.objects.get(user=request.user)
        # if not self.queryset.cart_products.count():
        #     return redirect(reverse('accounts:user_account', kwargs={'slug':request.user.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CreateOrderView(LoginRequiredMixin, AccountMixin, FormView, Orders_service):
    model = Order
    template_name = 'orders/order_create.html'
    form_class = CreateOrderForm
    success_url = None

    def dispatch(self, request, *args, **kwargs):
        self.success_url = reverse('orders:create_order', kwargs={
                                   'pk': request.user.pk})
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        bound_form = self.form_class(request.POST)

        if bound_form.is_valid():
            order = bound_form.save(commit=False)
            order = self.create_order(request, order)

        return redirect(reverse('accounts:user_account',  kwargs={'pk': request.user.pk}))


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'

    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs['id'])
