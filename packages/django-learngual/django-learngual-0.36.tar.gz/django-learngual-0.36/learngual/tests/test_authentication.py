from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.test import APIClient, APIRequestFactory

from ..authentication import LearngualAuthentication, LearngualFakeAuthentication
from .request_mock import requests as mock_requests

factory = APIRequestFactory()
User = get_user_model()


@patch("iam_service.learngual.authentication.get_user")
@patch("requests.get", return_value=mock_requests.get)
def test_authentication(mock_req, get_user, user: User, client: APIClient):  # type: ignore
    # Create a sample request
    get_user.return_value = user
    mock_req.json.return_value = {
        "account": {
            "id": "84bcaf2972",
            "cover_photo": None,
            "profile_photo": None,
            "type": "PERSONNAL",
            "metadata": {},
            "created_at": "2023-01-13T16:33:52.084540Z",
            "updated_at": "2023-01-13T16:33:52.084576Z",
        },
        "email": "Bulah53@gmail.com",
        "first_name": "Caitlyn",
        "id": "40e0e7013f",
        "last_name": "Marquardt",
        "registration_step": "REGISTRATION_COMPLETED",
        "username": "Eloisa.Senger42",
    }
    request = factory.get("/api/my-endpoint/")

    # Add the custom header to the request
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    token += (
        ".eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiaWF0IjoxNjIzMzQ5NTMwLCJleHAiOjE2MjMzNTM5MzB9"
    )
    token += ".6FcybZUxW1szsiavTbF-MfnEvC57lU3J0C1dd6nM2O0"
    request.META["HTTP_AUTHORIZATION"] = "Bearer " + token

    # Authenticate the request

    # Create an instance of the custom authentication class
    auth = LearngualAuthentication()

    # Authenticate the request using the custom authentication class
    authenticated = auth.authenticate(request)

    # Assert that authentication is successful
    assert authenticated[0] == user
    assert authenticated[1] == token


def test_fake_authentication_account(personal_account: object, client: APIClient):  # type: ignore

    request = factory.get("/api/my-endpoint/")

    request.META["HTTP_ACCOUNT"] = personal_account.id

    # Authenticate the request

    # Create an instance of the custom authentication class
    auth = LearngualFakeAuthentication()

    # Authenticate the request using the custom authentication class
    authenticated = auth.authenticate(request)
    assert authenticated, "authentication return None"

    # Assert that authentication is successful
    assert authenticated[0] == getattr(personal_account, "owner", None) or getattr(
        personal_account, "user", None
    )
    assert authenticated[0].account == personal_account
    assert authenticated[1] in ["fake_token", ""]


def test_fake_authentication_user(user: User):  # type: ignore

    request = factory.get("/api/my-endpoint/")

    request.META["HTTP_ACCOUNT"] = user.id

    # Authenticate the request

    # Create an instance of the custom authentication class
    auth = LearngualFakeAuthentication()

    # Authenticate the request using the custom authentication class
    authenticated = auth.authenticate(request)
    assert authenticated, "authentication return None"

    # Assert that authentication is successful
    assert authenticated[0] == user
    assert authenticated[0].account is None
    assert authenticated[1] in ["fake_token", ""]


def test_authentication_service_key(settings):

    request = factory.get("/api/my-endpoint/")

    # Add the custom header to the request

    request.META["HTTP_SERVICE_KEY"] = settings.LEARNGUAL_SERVICE_API_KEY

    # Authenticate the request

    # Create an instance of the custom authentication class
    auth = LearngualAuthentication()

    # Authenticate the request using the custom authentication class
    authenticated = auth.authenticate(request)

    # Assert that authentication is successful
    assert getattr(authenticated[0], "is_service", None)
    assert authenticated[1] == settings.LEARNGUAL_SERVICE_API_KEY


def test_authentication_invalid_service_key(settings):

    request = factory.get("/api/my-endpoint/")

    # Add the custom header to the request

    request.META["HTTP_SERVICE_KEY"] = "hshsggfaas"

    # Authenticate the request

    # Create an instance of the custom authentication class
    auth = LearngualAuthentication()

    try:
        # Authenticate the request using the custom authentication class
        authenticated = auth.authenticate(request)
        assert authenticated
    except exceptions.AuthenticationFailed:
        assert True
