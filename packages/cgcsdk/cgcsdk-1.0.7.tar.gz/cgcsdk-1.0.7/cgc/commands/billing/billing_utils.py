import click
import datetime
import sys
from tabulate import tabulate
from cgc.utils.message_utils import (
    prepare_error_message,
)


def verify_input_datetime(*args):
    try:
        for arg in args:
            datetime.datetime.strptime(arg, "%d-%m-%Y")
    except ValueError:
        click.echo(prepare_error_message("Incorrect date format, should be DD-MM-YYYY"))
        sys.exit()


def _get_costs_list_for_user(costs_list: list):
    """Method to format data in costs list to be displayed in a table and calculate user cost


    :param costs_list: list of costs for user
    :type costs_list: list
    :return: formatted list of costs and total cost for user
    :rtype: user_costs_list_to_print: list, total_user_cost: float
    """
    user_costs_list_to_print = []
    total_user_cost = 0
    for cost in costs_list:
        rent_start = cost["rent_start_cost"]
        rent_end = cost["rent_end_cost"]
        rent_time = f"{int(cost['rent_time_cost'])} s"
        rent_cost = f"{float(cost['cost_total']):.2f} pln"
        resources = cost["resources"]
        name = resources["name"]
        rent_type = cost["type"]
        if rent_type == "events_resource":
            entity = resources["entity"]
        elif rent_type == "events_volume":
            entity = "volume"
        else:
            entity = "ERROR"
        total_user_cost += float(cost["cost_total"])
        row_list = [entity, name, rent_start, rent_end, rent_time, rent_cost]
        user_costs_list_to_print.append(row_list)
    if costs_list:
        user_costs_list_to_print.sort(key=lambda d: f"{d[0]} {d[2]}")
    return user_costs_list_to_print, total_user_cost


def get_billing_status_message(user_list: list):
    """Prints billing status for all users in a pretty table

    :param user_list: list of users with costs
    :type user_list: list
    """
    message = ""
    for user in user_list:
        user_id = user["user_id"]
        costs_list = user["details"]
        costs_list_to_print, _user_cost = _get_costs_list_for_user(costs_list)
        list_headers = _get_status_list_headers()
        message += f"Billing status for user: {user_id}\n"
        message += tabulate(costs_list_to_print, headers=list_headers)
        message += f"\n\nSummary user cost: {float(_user_cost):.2f} pln\n\n"
    return message

    # "status": "Success",
    # "reason": "BILLING_INVOICE",
    # "details": {
    #     "namespace": "pytest",
    #     "cost_total": 0,
    #     "invoice": [
    #         {
    #             "user_id": "e57c8668-6bc3-47c7-85de-903bfc3772b7",
    #             "month": 11,
    #             "year": 2022,
    #             "cost_total": 0,
    #             "details": [],
    #         }
    #     ],
    #     "date_requested": {"year": 2022, "month": 11},


def _get_status_list_headers():
    """Generates headers for billing status command

    :return: list of headers
    :rtype: list
    """
    return ["entity", "name", "start", "end", "time", "cost"]


# TODO: refactor to use: tabulate_a_response(data: list) -> str:
def get_table_compute_stop_events_message(event_list: list):
    """Prints compute stop events info

    :param event_list: raw list of events
    :type event_list: list
    """
    message = "Compute stop events:"
    event_list_headers = ["id", "name", "entity", "date created"]
    event_list_to_print = []
    for event in event_list:
        event_id = event["event_id"]
        event_name = event["event_name"]
        event_date = event["date_created"]
        event_entity = event["entity"]
        row_list = [event_id, event_name, event_entity, event_date]
        event_list_to_print.append(row_list)
    message += tabulate(event_list_to_print, headers=event_list_headers)
    return message


# TODO: refactor to use: tabulate_a_response(data: list) -> str:
def get_table_volume_stop_events_message(event_list: list):
    """Prints volume stop events info

    :param event_list: raw list of events
    :type event_list: list
    """
    message = "Volume stop events:"
    event_list_headers = [
        "id",
        "name",
        "disks type",
        "access type",
        "size",
        "date created",
    ]
    event_list_to_print = []
    for event in event_list:
        event_id = event["event_id"]
        volume_name = event["volume_name"]
        event_date = event["date_created"]
        disks_type = event["disks_type"]
        access_type = event["access_type"]
        size = event["size"]
        row_list = [event_id, volume_name, disks_type, access_type, size, event_date]
        event_list_to_print.append(row_list)
    message += tabulate(event_list_to_print, headers=event_list_headers)
    return message
