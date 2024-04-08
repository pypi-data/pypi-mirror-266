import importlib
import logging
import os
from logging import getLogger

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions
from rest_framework.request import Request

logger = getLogger(__file__)

User = get_user_model()

LEARNGUAL_SERVICE_API_KEY = getattr(
    settings, "LEARNGUAL_SERVICE_API_KEY", None
) or os.getenv("LEARNGUAL_SERVICE_API_KEY", None)

"""
Configure authentication class
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        ...
        "iam_service.users.authentication.LearngualAuthentication",
        ...
    ),
    ...
}

LEARNGUAL_AUTH_RETRIEVE_URL=<auth server url to authenticate if user is login>
LEARNGUAL_AUTH_TEST_MODE=<True or False used for testing provide dummy data to authenticate user>
LEARNGUAL_AUTH_GET_USER=<dot path to the callable >

Data = {
    "account": {
        "id": "84bcaf2972",
        "cover_photo": None,
        "profile_photo": None,
        "type": "PERSONNAL",
        "metadata": {},
        "created_at": "2023-01-13T16:33:52.084540Z",
        "updated_at": "2023-01-13T16:33:52.084576Z"
    },
    "email": "Bulah53@gmail.com",
    "first_name": "Caitlyn",
    "id": "40e0e7013f",
    "last_name": "Marquardt",
    "registration_step": "REGISTRATION_COMPLETED",
    "username": "Eloisa.Senger42"
}

def get_user(data:Data):

    print("data in get user")
    return get_user_model().objects.get_or_create()

"""


user_test_data = {
    "account": {
        "id": "84bcaf2972",
        "cover_photo": None,
        "profile_photo": None,
        "type": "PERSONAL",
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


def load_callable(path: str) -> object | None:
    paths = path.split(".")
    modules = importlib.import_module(".".join(paths[:-1]))
    result = getattr(modules, paths[-1], None)
    if not result:
        logger.warning("Module does no exists. path: %s", path)
    return result


LEARNGUAL_AUTH_RETRIEVE_URL = getattr(settings, "LEARNGUAL_AUTH_RETRIEVE_URL", None)
LEARNGUAL_AUTH_GET_USER = getattr(settings, "LEARNGUAL_AUTH_GET_USER", None)
LEARNGUAL_AUTH_ACCOUNT_MODEL_PATH = getattr(
    settings, "LEARNGUAL_AUTH_ACCOUNT_MODEL_PATH", None
)


assert (
    LEARNGUAL_AUTH_RETRIEVE_URL
), "LEARNGUAL_AUTH_RETRIEVE_URL must be provided in the settings."
assert (
    LEARNGUAL_AUTH_GET_USER
), "LEARNGUAL_AUTH_GET_USER must be provided in the settings."


get_user: callable = load_callable(LEARNGUAL_AUTH_GET_USER)
assert get_user, "No callable exists in path:%s" % LEARNGUAL_AUTH_GET_USER


class LearngualAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    @classmethod
    def get_http_headers(cls, request: Request):
        headers = {
            key.lower().lstrip("http_"): value
            for key, value in request.META.items()
            if key.lower().startswith("http_")
        }
        return headers

    @classmethod
    def get_query_str(cls, request: Request):
        return "?{query}".format(query=request.META.get("QUERY_STRING", ""))

    def authenticate(self, request):
        # this is for test mode

        service_key = str(
            request.META.get("HTTP_SERVICE_KEY", "")
            or request.GET.get("service-key", "")
            or request.GET.get("_service-key", "")
        )
        if service_key:
            logger.info("authentication send with service account")
            if service_key == LEARNGUAL_SERVICE_API_KEY:
                service_user = User(id="service", username="service")
                service_user.is_service = True
                return service_user, service_key
            logger.warn("invalid service key")
            msg = _("Invalid service key")
            raise exceptions.AuthenticationFailed(msg)

        header = self.get_header(request)
        logger.info(
            "retrieve required authentication header during authentication -> %s",
            header,
        )
        if not header.get("authorization"):
            logger.warn("no authorization")
            return None
        headers = self.get_http_headers(request)
        logger.info("get django request header for forwarding -> %s", headers)

        query_str = self.get_query_str(request)
        logger.info("query string for forwarding -> %s", query_str)
        logger.info(f"{LEARNGUAL_AUTH_RETRIEVE_URL =}")
        res = requests.get(LEARNGUAL_AUTH_RETRIEVE_URL + query_str, headers=headers)
        if not res.ok:
            logging.warn("request to IAM service did not go through")
            return None
        logging.info("verify auth response data -> %s", res.content)
        res_data = res.json()
        logging.info("verify auth response json data -> %s", res_data)
        return (
            get_user(res_data),
            header.get("api_key") or header.get("authorization").split(" ")[-1],
        )

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        account_id = str(
            request.META.get("HTTP_ACCOUNT", "")
            or request.META.get("HTTP_X_ACCOUNT", "")
        )
        api_key = str(
            request.META.get("HTTP_API_KEY", "")
            or request.META.get("HTTP_X_API_KEY", "")
        )
        service_key = str(
            request.META.get("HTTP_SERVICE_KEY", "")
            or request.META.get("HTTP_X_SERVICE_KEY", "")
            or request.GET.get("service-key", "")
            or request.GET.get("_service-key", "")
        )
        authorization = str(request.META.get("HTTP_AUTHORIZATION", ""))

        return dict(
            account_id=account_id,
            api_key=api_key,
            authorization=authorization,
            service_key=service_key,
        )


def default_user_authentication_rule(user):
    # Prior to Django 1.10, inactive users could be authenticated with the
    # default `ModelBackend`.  As of Django 1.10, the `ModelBackend`
    # prevents inactive users from authenticating.  App designers can still
    # allow inactive users to authenticate by opting for the new
    # `AllowAllUsersModelBackend`.  However, we explicitly prevent inactive
    # users from authenticating to enforce a reasonable policy and provide
    # sensible backwards compatibility with older Django versions.
    return user is not None and user.is_active


class LearngualFakeAuthentication(authentication.BaseAuthentication):
    """
    A fake authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    It simulates authentication by the IAM service, but uses the "account"
    header to internally retrieve the account
    """

    www_authenticate_realm = "api"
    media_type = "application/json"
    account_model: type[models.Model] | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()
        self.account_model = load_callable(LEARNGUAL_AUTH_ACCOUNT_MODEL_PATH)

    @classmethod
    def get_http_headers(cls, request: Request):

        headers = dict()
        if request:
            for key, value in request.META.items():
                if key.lower().startswith("http_"):
                    headers[key.lower().lstrip("http_")] = value
        return headers

    @classmethod
    def get_query_str(cls, request: Request):
        return "?{query}".format(query=request.META.get("QUERY_STRING", ""))

    def authenticate(self, request):
        logger.info("authenticate() starting")
        header = self.get_header(request)

        headers = self.get_http_headers(request)

        account_or_user_id = headers.get("account")
        # logger.info("account_or_user_id: %s", account_or_user_id)
        account = None
        user = None
        if self.account_model:
            account = self.account_model.objects.filter(id=account_or_user_id).first()
            if account:
                logger.info("account exist: %s", account)
                user = getattr(account, "owner", None) or getattr(account, "user", None)
                user.account = account

        if not account:
            logger.info("account not found")
            user = self.user_model.objects.filter(id=account_or_user_id).first()
            if user:
                logger.info("user exists: %s", user)
                user.account = None

        if not user:
            return None
        logger.info("authenticate() completed")
        return (
            user,
            header.get("api_key")
            or (header.get("authorization").split(" ") or ["fake_token"])[-1],
        )

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        account_id = str(request.META.get("HTTP_ACCOUNT", ""))
        api_key = str(request.META.get("HTTP_API_KEY", ""))
        authorization = str(request.META.get("HTTP_AUTHORIZATION", ""))

        return dict(account_id=account_id, api_key=api_key, authorization=authorization)
