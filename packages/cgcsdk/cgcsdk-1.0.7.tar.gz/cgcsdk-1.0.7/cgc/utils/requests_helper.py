import requests
import urllib3
import urllib3.exceptions
import ssl
import click
import sys

from enum import Enum

from cgc.utils.consts.env_consts import API_SECURE_CONNECTION
from cgc.telemetry.basic import increment_metric
from cgc.utils.message_utils import prepare_error_message
from cgc.utils.consts.message_consts import (
    TIMEOUT_ERROR,
    UNKNOWN_ERROR,
    CONNECTION_ERROR,
    CERTIFICATE_ERROR,
)

urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)


class EndpointTypes(Enum):
    get = requests.get
    post = requests.post
    delete = requests.delete


def _process_endpoint_kwargs(**kwargs):
    if not "timeout" in kwargs.keys():
        kwargs["timeout"] = 30
    return kwargs


def _call_rest_endpoint(request: EndpointTypes, **kwargs):
    kwargs = _process_endpoint_kwargs(**kwargs)
    return request(**kwargs)


def _call_rest_ssl_endpoint(request: EndpointTypes, **kwargs):
    kwargs = _process_endpoint_kwargs(**kwargs)
    return request(
        **kwargs, verify=False
    )  # TODO: protect against man-in-the-middle attacks


def call_api(request: EndpointTypes, **kwargs):
    try:
        if API_SECURE_CONNECTION == "yes":
            return _call_rest_ssl_endpoint(request=request, **kwargs)
        else:
            return _call_rest_endpoint(request=request, **kwargs)
    except requests.exceptions.ReadTimeout:
        increment_metric(metric="client.timeout", is_error=True)
        click.echo(prepare_error_message(TIMEOUT_ERROR))
        sys.exit()

    except requests.exceptions.ConnectionError:
        increment_metric(metric="client.connection", is_error=True)
        click.echo(prepare_error_message(CONNECTION_ERROR))
        sys.exit()
    except OSError:
        increment_metric(metric="client.certificate", is_error=True)
        click.echo(prepare_error_message(CERTIFICATE_ERROR))
        sys.exit()
    except:
        increment_metric(metric="client.unhandled", is_error=True)
        click.echo(prepare_error_message(UNKNOWN_ERROR))
        sys.exit()  # all other errors
