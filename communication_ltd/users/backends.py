from django.contrib.auth.backends import ModelBackend
from .models import Customer
from .utils import check_password

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            customer = Customer.objects.get(email=username)
        except Customer.DoesNotExist:
            return None
        
        if customer and check_password(customer.password, password):
            return customer
        return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None
