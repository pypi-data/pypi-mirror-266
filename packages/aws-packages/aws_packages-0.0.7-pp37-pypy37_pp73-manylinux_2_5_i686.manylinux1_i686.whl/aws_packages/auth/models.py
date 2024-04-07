from dataclasses import dataclass


@dataclass
class AuthorizationRequest:
    """Authorization request model"""

    Authorization: str

    @property
    def token(self):
        return self.Authorization


@dataclass
class AuthenticationRequest:
    """Authentication request model"""

    user: str
    authcode: str


@dataclass
class User:
    """User model."""

    principal: str
