import re
from django.core.checks import messages
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.db.models import query
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, PasswordResetConfirmView
from django.contrib.auth import login, logout
from django.views.generic import TemplateView, DetailView, UpdateView
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth import get_user_model
from .forms import *
from .mixins import SuccessUrlMixin
from .models import Account



def login_excluded(redirect_to):
    def _method_wrapper(view_method):
        def _arguments_wrapper(self_parametr, request, *args, **kwargs):
            if request.user.is_authenticated and request.user.pk == int(kwargs['pk']):
                return view_method(self_parametr, request, *args, **kwargs)
            return redirect('shop:home')
        return _arguments_wrapper
    return _method_wrapper


# Create your views here.

class LoginFormView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LogInAccount
    success_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_url'] = self.success_url
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('next'):
            self.success_url = request.GET.get('next')
        else:
            self.success_url = reverse_lazy('shop:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user(),
              backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponseRedirect(self.success_url)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class RegisterView(CreateView):
    template_name = 'accounts/register.html'
    form_class = RegisterAccount
    success_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_url'] = self.success_url
        print(self.success_url)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('next'):
            self.success_url = request.GET.get('next')
        else:
            self.success_url = reverse_lazy('shop:home')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        bound_form = RegisterAccount(request.POST)

        if bound_form.is_valid():
            user = bound_form.save()
            user.email = bound_form.cleaned_data['email']
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            print(self.success_url)
            return HttpResponseRedirect(self.success_url)

        else:
            return render(request, self.template_name, context={'form': bound_form})


class UpdateAccount(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Account
    fields = []
    template_name = 'accounts/update_account.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.fields.append(kwargs['field'])
        return super().dispatch(request, *args, **kwargs)
    
    


class AccountDetailView(LoginRequiredMixin, SuccessUrlMixin ,DetailView):
    model = User
    template_name = 'accounts/account.html'
    login_url = reverse_lazy('shop:home')

    def get(self, request, *args, **kwargs):
        if self.object != request.user:
            return redirect(reverse_lazy('shop:home'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.account.cart:
            context['latest_cart_products'] = self.object.account.cart.cart_products.all()[
                :4]

        if self.object.account.orders.all():
            context['orders'] = self.object.account.orders.all()[:4]

        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = self.model.objects.get(pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
