from django.db.models.fields import SlugField
from shop.const import CT_MODEL_CLASS, get_product_models
from .models import Cart, CartProduct
from accounts.models import Order
from django.contrib.contenttypes.models import ContentType


class Orders_service:
    def is_product_added(self, model_name, product_slug, user_cart):
        content_type = ContentType.objects.get(model=model_name)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = None
        
        try:
            cart_product = user_cart.cart_products.get(object_id=product.id, content_type=content_type, cart = user_cart)

        except Exception as e:
            cart_product = None
        
        return cart_product
        
        
        
    def add_new_product(self, model_name, product_slug, user_cart):
        
        cart_product = self.is_product_added(model_name, product_slug, user_cart)
        if not cart_product:
            content_type = ContentType.objects.get(model=model_name)
            product = content_type.model_class().objects.get(slug=product_slug)
            cart_product = CartProduct.objects.create(object_id=product.id, content_type=content_type, cart = user_cart)
            user_cart.cart_products.add(cart_product)

        else:
            cart_product.quantity += 1
            cart_product.calc_finale_price()
            cart_product.save()
     
        

    def update_product_quantity(self, model_name, product_slug, user_cart, value=1):
        cart_product = self.is_product_added(model_name, product_slug, user_cart)
        cart_product.quantity = value
        cart_product.save()
        
        return cart_product
    
    def delete_product(self, model_name, product_slug, user_cart):
        cart_product = self.is_product_added(model_name, product_slug, user_cart)
        cart_product.delete()
        
        return True
    
    
    def create_order(self, request, order):
        order.customer = request.user.account
        order.final_price = request.user.account.cart.get_final_price()
        order.save()
        
        
        for product in request.user.account.cart.cart_products.all():
            order.cart.add(product)

        order.save()
        request.user.account.cart.cart_products.clear()
        request.user.account.orders.add(order)  
        return order
