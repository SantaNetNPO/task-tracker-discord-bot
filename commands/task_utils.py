import yaml
from yaml.loader import SafeLoader
from functools import reduce

import settings


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


async def get_no_of_subtasks(current_task, message):
    """
    Crawl through the task tree and return the number of subtasks.
    """
    found_department = False
    found_objective = False
    found_task = False
    for department in get_task_config()["departments"]:
        if department["id"] == current_task["department_id"]:
            found_department = True
            for objective in department["objectives"]:
                if objective["id"] == current_task["objective_id"]:
                    found_objective = True
                    for task in objective["tasks"]:
                        if task["id"] == current_task["task_id"]:
                            found_task = True
                            return len(task["subtasks"])

    if not found_department:
        await message.channel.send(f"Department not found. {settings.ADMIN_ROLE_MENTION} please look into this.")
    if not found_objective:
        await message.channel.send(f"Task Objective not found. {settings.ADMIN_ROLE_MENTION} please look into this.")
    if not found_task:
        await message.channel.send(f"Task not found. {settings.ADMIN_ROLE_MENTION} please look into this.")
    return False


async def find_next_task(current_task, message):
    """
    Based on current_task parameters find the next task, and possibly the
    next objective.
    """
    found_department = False
    found_objective = False
    found_task = False
    for department in get_task_config()["departments"]:
        if department["id"] == current_task["department_id"]:
            found_department = True
            for objective_index, objective in enumerate(department["objectives"]):
                if objective["id"] == current_task["objective_id"]:
                    found_objective = True
                    for task_index, task in enumerate(objective["tasks"]):
                        if task["id"] == current_task["task_id"]:
                            found_task = True
                            if task_index < len(objective["tasks"]) - 1:
                                return (
                                    objective["id"],
                                    objective["tasks"][task_index + 1]["id"],
                                )
                            if objective_index < len(department["objectives"]) - 1:
                                return (
                                    department["objectives"][objective_index + 1]["id"],
                                    department["objectives"][objective_index + 1]["tasks"][0]["id"],
                                )
                            return (True, True)

    if not found_department:
        await message.channel.send(f"Department not found. {settings.ADMIN_ROLE_MENTION} please look into this.")
    if not found_objective:
        await message.channel.send(f"Task Objective not found. {settings.ADMIN_ROLE_MENTION} please look into this.")
    if not found_task:
        await message.channel.send(f"Task not found. {settings.ADMIN_ROLE_MENTION} please look into this.")
    return (False, False)
