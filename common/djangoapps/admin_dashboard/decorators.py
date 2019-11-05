from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from student.models import UserSites, UserProfile

def takamol_admin(f):
    def wrap(request, *args, **kwargs):
        try:
            UserSites.objects.get(user=request.user, takamol_admin=True)
        except ObjectDoesNotExist:
            return render_to_response("admin_dashboard/no_permission.html")

        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def site_admin(f):
   def wrap(request, *args, **kwargs):
       try:
           UserSites.objects.get(user=request.user,site=request.site,site_admin=True)

       except ObjectDoesNotExist:
           return render_to_response("admin_dashboard/no_permission.html")

       return f(request, *args, **kwargs)

   wrap.__doc__ = f.__doc__
   wrap.__name__ = f.__name__
   return wrap