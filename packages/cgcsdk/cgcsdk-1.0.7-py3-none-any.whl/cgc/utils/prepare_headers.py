from cgc.utils.config_utils import read_from_cfg
from cgc.utils.consts.env_consts import API_URL, CGC_SECRET
from cgc.commands.auth import auth_utils
from cgc.utils.message_utils import key_error_decorator_for_helpers


def load_user_api_keys():
    """Based on configuration getter creates pair of API keys

    :return: api_key and api_secret
    :rtype: list of strings
    """
    return read_from_cfg("api_key"), read_from_cfg("api_secret")


@key_error_decorator_for_helpers
def get_api_url_and_prepare_headers():
    """Loads API_URL and user api keys into single function. Mend to be used as single point of truth for all endpoints except register - due to different Content-Type header

    :return: API_URL and headers
    :rtype: string and dict
    """
    api_key, api_secret = load_user_api_keys()
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "accept": "application/json",
        "api-key": api_key,
        "api-secret": api_secret,
        "comtegra-cgc": CGC_SECRET,
    }
    return API_URL, headers


def get_url_and_prepare_headers_register(user_id: str, access_key: str):
    """Creates and returns url and headers for register request.

    :return: url, headers
    :rtype: string and dict
    """
    url = f"{API_URL}/v1/api/user/register?user_id={user_id}&access_key={access_key}"
    headers = {
        "accept": "application/json",
        "comtegra-cgc": CGC_SECRET,
        "Content-Type": "octet-stream",
    }
    return url, headers


def get_url_and_headers_jwt_token():
    url = f"{API_URL}/v1/api/user/create/token"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    return url, headers


@key_error_decorator_for_helpers
def prepare_headers_api_key(user_id: str = None, password: str = None):
    """Prepares headers for create API key request.

    :return: headers in a for of dictionary
    :rtype: dict
    """
    headers = {
        "accept": "application/json",
        "comtegra-cgc": CGC_SECRET,
        "Authorization": f"Bearer {auth_utils.get_jwt(user_id, password)}",
    }
    return headers


def get_api_url_and_prepare_headers_version_control():
    """Prepares headers for version control request.

    :return: url and headers in a for of dictionary
    :rtype: string, dict
    """
    url = f"{API_URL}/v1/api/info/version"
    headers = {
        "accept": "application/json",
        "comtegra-cgc": CGC_SECRET,
        "Content-Type": "application/json",
    }
    return url, headers
