from typing import List
from cgc.utils import quick_sort
from cgc.utils.config_utils import read_from_cfg
from tabulate import tabulate


def table_of_user_context_files(config_files: List[str]):
    # print tabulate of: [context NR | namespace | user_id]
    headers = ["Context No.", "Namespace", "User ID"]
    contexts = []
    contexts_nrs = []
    for file in config_files:
        file_context = []
        file_context.append(
            int(file.split(".")[0]) if file != "cfg.json" else 1
        )  # should never throw exception with good config_file list
        contexts_nrs.append(file_context[0])
        file_data = read_from_cfg(None, file)
        values_to_read = ["namespace", "user_id"]
        for k in values_to_read:
            try:
                value = file_data[k]
            except KeyError:
                value = None
            file_context.append(value)
        contexts.append(file_context)

    contexts_nrs_sorted = quick_sort(contexts_nrs)
    contexts_sorted = []
    for context in contexts_nrs_sorted:
        contexts_sorted.append(contexts[contexts_nrs.index(context)])

    return tabulate(contexts_sorted, headers=headers)
