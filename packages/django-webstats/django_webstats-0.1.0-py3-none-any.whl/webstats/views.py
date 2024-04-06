from django.http import HttpResponse
from django.views import View
from .mixins import RecordVisitMixin


class TestView(RecordVisitMixin, View):
    def get(self, request):
        return HttpResponse("all good")
