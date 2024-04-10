import time

import requests

FUNCTION_CONTROLLER_DEV_TOKEN_SCOPE = "function_dev function_call"  # nosec
TOKEN_ISSUER = "https://login.contact-cloud.com/realms/contact"  # nosec
TOKEN_URL_EXTENSION = "/protocol/openid-connect/token"  # nosec


class CredentialsInvalid(Exception):
    pass


def authenticate_keycloak(client_id: str, client_secret: str) -> (str, int):
    """
    Connects with the given credentials to KeyCloak and fetch an access token
    return: a jwt token and unix timestamp when the token will expire
    """
    payload = {
        "grant_type": "client_credentials",
        "scope": FUNCTION_CONTROLLER_DEV_TOKEN_SCOPE,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        TOKEN_ISSUER + TOKEN_URL_EXTENSION,
        headers=headers,
        data=payload,
        auth=(client_id, client_secret),
        timeout=60,
    )

    if response.status_code == 401:
        raise CredentialsInvalid
    if response.status_code != 200:
        raise ValueError(f"Token endpoint returned status code {response.status_code}")

    response_content = response.json()
    return (
        response_content["access_token"],
        int(response_content["expires_in"]) + time.time(),
    )
