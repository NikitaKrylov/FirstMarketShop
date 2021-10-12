from django.urls import reverse, reverse_lazy


class AccountMixin:
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account'] = self.user.account
        context['cart'] = self.user.account.cart
        return context


class SuccessUrlMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.GET.get('next'):
            self.success_url = request.GET.get('next')
        else:
            self.success_url = reverse_lazy('shop:home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_url'] = self.success_url
        
        return context
