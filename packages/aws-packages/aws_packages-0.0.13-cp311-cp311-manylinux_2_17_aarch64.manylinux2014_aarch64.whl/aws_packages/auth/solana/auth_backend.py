"""Authentication backends.

"""

from aws_packages.auth.auth_backend_base import AuthBackendBase
from aws_packages.auth.models import AuthenticationRequest, User
from aws_packages.auth.tokens import AccessToken


class SolanaAuthBackend(AuthBackendBase):
    """Authentication backend with Solana Canister"""

    def __init__(self, url: str):
        self._url = url

    def authenticate(self, login_request: AuthenticationRequest) -> User:
        """Authenticate the request and returns an authenticated User"""

        # solana sdk call and authenticate or raise exception

        return User(principal=login_request.user)

    def authenticate_with_token(self, token: str):
        """Authenticate user using jwt token and return status"""
        print("token : ", token)
        AccessToken(token_string=token)

    def get_access_token(self, user: User) -> str:
        """Get the access for the given user"""
        token = AccessToken()
        return token.get_access_token(user)


solana_auth_backend = SolanaAuthBackend(
    url="https://ic0.app",
)

if __name__ == "__main__":
    _auth_backend = SolanaAuthBackend(
        url="https://ic0.app",
    )

    request = AuthenticationRequest(
        user="4cay5-ew3bs-vr6yl-7iffu-67doc-l655v-dluy7-qplpx-7pkio-er5rt-uqe",
        authcode="",
    )
    user = solana_auth_backend.authenticate(request)
    print(user)
