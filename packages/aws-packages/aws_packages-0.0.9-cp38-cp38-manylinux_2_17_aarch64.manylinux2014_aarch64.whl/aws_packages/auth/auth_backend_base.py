from aws_packages.auth.models import AuthenticationRequest, User


class AuthBackendBase:
    """Base class for authentication backends"""

    def authenticate(self, request: AuthenticationRequest) -> User:
        """Authenticate the request and returns an authenticated User"""

        raise NotImplementedError("authenticate not implemented")

    def authenticate_with_token(self, token: str) -> bool:
        """Authenticate user using jwt token and return status"""
        raise NotImplementedError("authenticate_with_token not implemented")

    def get_access_token(self, user: User) -> str:
        """Get the access for the given user"""
        raise NotImplementedError("get_access_token not implemented")

    def get_refresh_token(self, user: User, token: str) -> str:
        """Get the refresh token for the given user"""
        raise NotImplementedError("get_refresh_token not implemented")
