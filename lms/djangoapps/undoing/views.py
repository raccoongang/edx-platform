from django.http import JsonResponse
import xmlrpclib

def destroy(request):
    server = xmlrpclib.Server('http://localhost:9001/RPC2')
    x = server.supervisor.shutdown()
    return JsonResponse({'succes': x})
