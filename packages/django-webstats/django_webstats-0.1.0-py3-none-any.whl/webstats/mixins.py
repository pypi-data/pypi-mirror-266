import logging
from django.urls import resolve
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Visit


def get_full_url_path(request):
    scheme = request.scheme + "://"
    host = request.get_host()
    full_path = request.get_full_path()
    full_url = scheme + host + full_path
    return full_url


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]  # pragma: no cover
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_full_url_name(request):
    match = resolve(request.path)
    url_name = match.url_name
    namespace = match.namespace
    full_url_name = f"{namespace}:{url_name}" if namespace else url_name
    return full_url_name


class RecordVisitMixin:
    def record_visit(self, request):
        visit = Visit()
        visit.url_path = get_full_url_path(request)
        visit.ip_address = get_client_ip(request)
        visit.view_name = get_full_url_name(request)
        try:
            visit.user = request.user
        except Exception as err:
            logging.warning(err)
            if "django.contrib.auth.models.AnonymousUser object" in repr(err):
                logging.info("User is anonymous. User logged as None.")
        visit.save()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.record_visit(request)
        return super(RecordVisitMixin, self).dispatch(request, *args, **kwargs)
