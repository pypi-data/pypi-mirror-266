import json
from http import HTTPStatus

from aws_lambda_powertools.event_handler import Response, content_types
from aws_lambda_powertools.event_handler.exceptions import BadRequestError

from aws_packages.auth.auth_backend_icp import icp_auth_backend
from aws_packages.auth.auth_backend_solana import solana_auth_backend
from aws_packages.auth.models import AuthenticationRequest, LoginResponse, User


def process_authenticate_request(request_body, auth_backend):
    if request_body is None:
        raise BadRequestError("No request body provided")

    request_obj = AuthenticationRequest(**json.loads(request_body))

    try:
        auth_user = auth_backend.authenticate(request_obj)
    except Exception as e:
        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,
            content_type=content_types.APPLICATION_JSON,
            body={"message": str(e)},
        )

    return Response(
        status_code=HTTPStatus.OK.value,
        content_type=content_types.APPLICATION_JSON,
        body=LoginResponse(
            access_token=auth_backend.get_access_token(auth_user)
        ).as_dict(),
    )


def process_icp_authenticate_request(request_body):
    return process_authenticate_request(request_body, icp_auth_backend)


def process_solana_authenticate_request(request_body):
    return process_authenticate_request(request_body, solana_auth_backend)
