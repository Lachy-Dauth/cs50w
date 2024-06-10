from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view_func
