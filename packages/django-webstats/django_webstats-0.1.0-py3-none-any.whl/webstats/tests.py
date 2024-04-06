from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from .models import Visit
from .views import TestView


User = get_user_model()


class TestViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_view(self):
        request = self.factory.get("/")
        view = TestView()
        view.request = request
        response = view.dispatch(request)
        self.assertEqual(response.status_code, 200)


class VisitModelTest(TestCase):
    def setUp(self):
        testuser = User.objects.create(username="testuser")
        self.visit = Visit.objects.create(
            url_path="http://localhost:8000",
            view_name="test_view",
            ip_address="127.0.0.1",
            user=testuser,
        )

    def test_str(self):
        visit = Visit.objects.get(view_name="test_view")
        self.assertEqual(
            self.visit.__str__(),
            f"{visit.url_path} at {visit.created} by {visit.ip_address}",
        )
