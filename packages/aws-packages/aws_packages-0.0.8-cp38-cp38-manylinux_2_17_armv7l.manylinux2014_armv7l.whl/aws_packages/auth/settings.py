from aws_packages.auth.auth_backend_base import AuthBackendBase

AUTH_SETTINGS = {"AUTH_BACKEND": None}


def get_auth_backend():
    return AUTH_SETTINGS["AUTH_BACKEND"]


def set_auth_backend(auth_backend: AuthBackendBase):
    AUTH_SETTINGS["AUTH_BACKEND"] = auth_backend
