import pytest
from django.test import RequestFactory
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.urls import reverse

from everycheese.users.forms import UserAdminChangeForm
from everycheese.users.models import User
from everycheese.users.views import (
    UserRedirectView,
    UserUpdateView,
)

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def dummy_get_response(self, request: HttpRequest):
        return None

    def test_get_success_url(
        self, user: User, request_factory: RequestFactory
    ):
        view = UserUpdateView()
        request = request_factory.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_success_url() == f"/users/{user.username}/"

    def test_get_object(
        self, user: User, request_factory: RequestFactory
    ):
        view = UserUpdateView()
        request = request_factory.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        form_data = {"name": "John Doe"}
        request = rf.post(
            reverse("users:update"), form_data
        )
        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user
        response = UserUpdateView.as_view()(request)
        user.refresh_from_db()

        assert response.status_code == 302
        assert user.name == form_data["name"]


class TestUserRedirectView:
    def test_get_redirect_url(
        self, user: User, request_factory: RequestFactory
    ):
        view = UserRedirectView()
        request = request_factory.get("/fake-url")
        request.user = user

        view.request = request

        assert (
            view.get_redirect_url() == f"/users/{user.username}/"
        )
