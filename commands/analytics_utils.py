import time


def update_task_stats(current_task, stats, user_doc_dict_stats):
    department = current_task["department_id"].replace("-", "_")
    objective = current_task["objective_id"].replace("-", "_")
    task = current_task["task_id"].replace("-", "_")

    if department not in user_doc_dict_stats:
        user_doc_dict_stats[department] = {}
    if objective not in user_doc_dict_stats[department]:
        user_doc_dict_stats[department][objective] = {}
    if task not in user_doc_dict_stats[department][objective]:
        user_doc_dict_stats[department][objective][task] = {}

    if objective not in stats:
        stats[objective] = {}
    if task not in stats[objective]:
        stats[objective][task] = {}
    if "average" not in stats[objective][task]:
        stats[objective][task]["average"] = 0
    if "least" not in stats[objective][task]:
        stats[objective][task]["least"] = 1630186453
    if "times_completed" not in stats[objective][task]:
        stats[objective][task]["times_completed"] = 0

    average_time = stats[objective][task]["average"]
    least_time = stats[objective][task]["least"]
    times_completed = stats[objective][task]["times_completed"]

    user_doc_dict_stats[department][objective][task]["time"] = time.time() - current_task["task_started_time"]

    stats[objective][task]["average"] = (
        average_time * times_completed + (time.time() - current_task["task_started_time"])
    ) / (times_completed + 1)
    stats[objective][task]["least"] = min(least_time, (time.time() - current_task["task_started_time"]))
    stats[objective][task]["times_completed"] = times_completed + 1

    return (stats, user_doc_dict_stats)


def update_subtask_stats(current_task, stats, user_doc_dict_stats):
    department = current_task["department_id"].replace("-", "_")
    objective = current_task["objective_id"].replace("-", "_")
    task = current_task["task_id"].replace("-", "_")
    subtask = str(current_task["subtask_no"]).replace("-", "_")

    if department not in user_doc_dict_stats:
        user_doc_dict_stats[department] = {}
    if objective not in user_doc_dict_stats[department]:
        user_doc_dict_stats[department][objective] = {}
    if task not in user_doc_dict_stats[department][objective]:
        user_doc_dict_stats[department][objective][task] = {}
    if subtask not in user_doc_dict_stats[department][objective][task]:
        user_doc_dict_stats[department][objective][task][subtask] = {}

    if objective not in stats:
        stats[objective] = {}
    if task not in stats[objective]:
        stats[objective][task] = {}
    if subtask not in stats[objective][task]:
        stats[objective][task][subtask] = {}
    if "average" not in stats[objective][task][subtask]:
        stats[objective][task][subtask]["average"] = 0
    if "least" not in stats[objective][task][subtask]:
        stats[objective][task][subtask]["least"] = 1630186453
    if "times_completed" not in stats[objective][task][subtask]:
        stats[objective][task][subtask]["times_completed"] = 0

    average_time = stats[objective][task][subtask]["average"]
    least_time = stats[objective][task][subtask]["least"]
    times_completed = stats[objective][task][subtask]["times_completed"]

    user_doc_dict_stats[department][objective][task][subtask]["time"] = (
        time.time() - current_task["subtask_started_time"]
    )

    stats[objective][task][subtask]["average"] = (
        average_time * times_completed + (time.time() - current_task["subtask_started_time"])
    ) / (times_completed + 1)
    stats[objective][task][subtask]["least"] = min(least_time, (time.time() - current_task["subtask_started_time"]))
    stats[objective][task][subtask]["times_completed"] = times_completed + 1

    return (stats, user_doc_dict_stats)
