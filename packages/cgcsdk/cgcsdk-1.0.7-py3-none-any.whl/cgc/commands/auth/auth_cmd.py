import click
import os
from cgc.commands.auth.auth_responses import (
    auth_register_response,
    login_successful_response,
)
from cgc.commands.auth.auth_utils import (
    auth_create_api_key_with_save,
    auth_delete_api_key,
    auth_list_api_keys,
)
from cgc.utils.prepare_headers import get_url_and_prepare_headers_register
from cgc.utils.cryptography import rsa_crypto
from cgc.utils.click_group import CustomCommand, CustomGroup
from cgc.utils.requests_helper import call_api, EndpointTypes
from cgc.utils.response_utils import (
    fill_missing_values_in_a_response,
    retrieve_and_validate_response_send_metric,
    tabulate_a_response,
)
from cgc.utils import (
    check_if_config_exist,
    require_confirm_loop,
    find_first_available_config_name,
)


@click.group("api-keys", cls=CustomGroup, hidden=False)
def api_keys_group():
    """
    Management of API keys.
    """
    pass


@click.command("register", cls=CustomCommand)
# @click.option("--user_id", "-u", "user_id", prompt=True)
# @click.option("--access_key", "-k", "access_key", prompt=True)
def auth_register(config_filename: str = "cfg.json"):
    """Register a user in system using user id and access key.\n
    Enabling/Disabling Telemetry sending is available, if set to yes CGC will send
    usage metrics for application improvements purposes.
    \f
    :param user_id: username received in invite
    :type user_id: str
    :param access_key: access key received in invite
    :type access_key: str
    :param telemetry_sending: if set to yes CGC will send
    usage metrics for application improvements purposes
    :type telemetry_sending: bool
    """

    if check_if_config_exist(config_filename):
        click.echo("Already registered.")
        require_confirm_loop("Do you want to add new context?")
        config_filename = find_first_available_config_name()

    user_id = input("User ID: ")
    access_key = input("Access key: ")
    url, headers = get_url_and_prepare_headers_register(user_id, access_key)
    metric = "auth.register"
    pub_key_bytes, priv_key_bytes = rsa_crypto.key_generate_pair()
    __payload = pub_key_bytes
    __res = call_api(
        request=EndpointTypes.post,
        url=url,
        headers=headers,
        data=__payload,
        allow_redirects=True,
    )
    click.echo(
        auth_register_response(
            retrieve_and_validate_response_send_metric(__res, metric, False),
            user_id,
            priv_key_bytes,
            config_filename,
        )
    )


@api_keys_group.command("create", cls=CustomCommand)
@click.option(
    "--user",
    "-u",
    "user_id",
    type=click.STRING,
    required=False,
)
@click.option(
    "--password",
    "-p",
    "password",
    type=click.STRING,
    required=False,
)
def api_keys_create(user_id: str, password: str):
    """Login a user in system using user id and password, then creates new API key pair and overwrites existing.
    \f
    :param user_id: user_id received in invite
    :type user_id: str
    :param password: password for the user
    :type password: str
    """
    api_key, secret = auth_create_api_key_with_save(user_id, password)
    click.echo(login_successful_response())
    click.echo(f"API key: {api_key}")
    click.echo(f"API secret: {secret}")


@api_keys_group.command("delete", cls=CustomCommand)
@click.argument("api_key", type=click.STRING, required=True)
def api_key_delete(api_key: str):
    """Delete API key.
    \f
    :param api_key: api_key to delete
    :type api_key: str
    """
    auth_delete_api_key(api_key)
    click.echo(f"API key {api_key} deleted.")


@api_keys_group.command("list", cls=CustomCommand)
def api_key_list():
    """List user_id api keys"""
    response = auth_list_api_keys()
    table = fill_missing_values_in_a_response(response)
    click.echo(tabulate_a_response(table))
