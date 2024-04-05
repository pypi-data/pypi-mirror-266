import click

from datetime import datetime

from cgc.commands.billing.billing_utils import verify_input_datetime
from cgc.commands.billing.billing_responses import (
    billing_status_response,
    billing_invoice_response,
    stop_events_resource_response,
    stop_events_volume_response,
)
from cgc.utils.prepare_headers import get_api_url_and_prepare_headers
from cgc.utils.response_utils import retrieve_and_validate_response_send_metric
from cgc.utils.click_group import CustomGroup, CustomCommand
from cgc.utils.requests_helper import call_api, EndpointTypes


@click.group("billing", cls=CustomGroup)
def billing_group():
    """
    Access and manage billing information.
    """
    pass


@billing_group.command("status", cls=CustomCommand)
def billing_status():
    """
    Shows billing status for user namespace
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/billing/status"
    metric = "billing.status"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        billing_status_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


def _get_previous_month():
    return datetime.now().month - 1 if datetime.now().month > 1 else 12


def _get_previous_year_if_required():
    return datetime.now().year - 1 if datetime.now().month == 1 else datetime.now().year


@billing_group.command("invoice", cls=CustomCommand)
@click.option(
    "--year",
    "-y",
    "year",
    prompt=True,
    type=int,
    default=_get_previous_year_if_required(),
)
@click.option(
    "--month",
    "-m",
    "month",
    prompt=True,
    type=click.IntRange(1, 12),
    default=_get_previous_month(),
)
def billing_invoice(year: int, month: int):
    """
    Opens invoice from given year and month
    """
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/billing/invoice?year={year}&month={month}"
    metric = "billing.invoice"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)

    click.echo(
        billing_invoice_response(
            year,
            month,
            retrieve_and_validate_response_send_metric(__res, metric),
        )
    )


@click.group("stop_events", cls=CustomGroup)
def stop_events_group():
    """
    List stop events information.
    """
    pass


@stop_events_group.command("resource")
@click.option(
    "--date_from",
    "-f",
    "date_from",
    prompt="Date from (DD-MM-YYYY)",
    default=datetime.now().replace(day=1).strftime("%d-%m-%Y"),
)
@click.option(
    "--date_to",
    "-t",
    "date_to",
    prompt="Date to (DD-MM-YYYY)",
    default=datetime.now().strftime("%d-%m-%Y"),
)
def stop_events_resource(date_from, date_to):
    verify_input_datetime(date_from, date_to)
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/billing/list_resource_stop_events?time_from={date_from}&time_till={date_to}"
    metric = "billing.stop_events.resource"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        stop_events_resource_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


@stop_events_group.command("volume")
@click.option(
    "--date_from",
    "-f",
    "date_from",
    prompt="Date from (DD-MM-YYYY)",
    default=datetime.now().replace(day=1).strftime("%d-%m-%Y"),
)
@click.option(
    "--date_to",
    "-t",
    "date_to",
    prompt="Date from (DD-MM-YYYY)",
    default=datetime.now().strftime("%d-%m-%Y"),
)
def stop_events_volume(date_from, date_to):
    verify_input_datetime(date_from, date_to)
    api_url, headers = get_api_url_and_prepare_headers()
    url = f"{api_url}/v1/api/billing/list_storage_stop_events?time_from={date_from}&time_till={date_to}"
    metric = "billing.stop_events.volume"
    __res = call_api(request=EndpointTypes.get, url=url, headers=headers)
    click.echo(
        stop_events_volume_response(
            retrieve_and_validate_response_send_metric(__res, metric)
        )
    )


billing_group.add_command(stop_events_group)
