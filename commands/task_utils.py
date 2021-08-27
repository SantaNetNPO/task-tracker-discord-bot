import yaml
from yaml.loader import SafeLoader

from functools import reduce


def get_task_config():
    """
    Loads the task configuration file.
    """
    with open("commands/tasks.yaml") as f:
        return yaml.load(f, Loader=SafeLoader)


def get_departments():
    """
    Returns a list of all departments.
    """
    return reduce(lambda x, y: [*x, y["id"]], get_task_config()["departments"], [])


def get_first_objective(department):
    """
    Returns the first objective of a department.
    """
    found = False
    for dept in get_task_config()["departments"]:
        if dept["id"] == department:
            found = True
            return dept["objectives"][0]
    if not found:
        return None
