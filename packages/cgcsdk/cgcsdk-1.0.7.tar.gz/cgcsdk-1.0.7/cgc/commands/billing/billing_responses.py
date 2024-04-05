import calendar
from cgc.commands.billing import (
    NoCostsFound,
    NoInvoiceFoundForSelectedMonth,
    NoResourceStopEvents,
    NoVolumeStopEvents,
)
from cgc.commands.billing.billing_utils import (
    get_billing_status_message,
    get_table_compute_stop_events_message,
    get_table_volume_stop_events_message,
)
from cgc.utils.message_utils import key_error_decorator_for_helpers


@key_error_decorator_for_helpers
def billing_status_response(data: dict) -> str:
    total_cost = data["details"]["cost_total"]
    namespace = data["details"]["namespace"]
    user_list = data["details"]["details"]
    if not user_list:
        raise NoCostsFound()
    message = get_billing_status_message(user_list)
    message += f"Total cost for namespace {namespace}: {total_cost:.2f} pln"
    return message


@key_error_decorator_for_helpers
def billing_invoice_response(year: int, month: int, data: dict) -> str:
    total_cost = float(data["details"]["cost_total"])
    namespace = data["details"]["namespace"]
    users_invoices_list = data["details"]["invoice"]
    if (
        not users_invoices_list or total_cost == 0
    ):  # TODO: total_cost == 0 is it correct thinking?
        raise NoInvoiceFoundForSelectedMonth(year, month)
    message = get_billing_status_message(users_invoices_list)
    message += f"Total cost for namespace {namespace} in {calendar.month_name[month]} {year}: {total_cost:.2f} pln"
    return message


@key_error_decorator_for_helpers
def stop_events_resource_response(data: dict) -> str:
    event_list = data["details"]["event_list"]
    if not event_list:
        raise NoResourceStopEvents()
    return get_table_compute_stop_events_message(event_list)


@key_error_decorator_for_helpers
def stop_events_volume_response(data: dict) -> str:
    event_list = data["details"]["event_list"]
    if not event_list:
        raise NoVolumeStopEvents()
    return get_table_volume_stop_events_message(event_list)
