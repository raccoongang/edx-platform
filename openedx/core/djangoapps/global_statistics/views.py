from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views.generic import View
from .models import TokenStorage


class ReceiveTokenView(View):
    """
    This view receives a secret token from the remote server and save it to DB.
    In the future, this will allow us to exchange data with a remote server.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ReceiveTokenView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        # Receive generated token from the remote server and save it to DB.
        try:
            received_data = self.request.POST
            secret_token = str(received_data.get('reverse_token'))
            token_object = TokenStorage.objects.get(pk=1)
            token_object.secret_token = secret_token
            token_object.save()
            return redirect('/')
        except ValueError:
            return redirect('/')
