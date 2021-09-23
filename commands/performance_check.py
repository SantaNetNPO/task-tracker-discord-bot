from google.cloud import firestore
from tabulate import tabulate
import os
import math

from commands.base_command import BaseCommand
from commands.task_utils import get_task_config
from commands.firebase_utils import check_registration_get_doc, get_user_current_task


class PerformanceCheck(BaseCommand):
    def __init__(self):
        description = "Check your task performance in relation to others"
        params = []
        alternate_names = ["perf", "perfcheck", "performance"]
        super().__init__(description, params, alternate_names)

    async def handle(self, params, message, client):
        department_stats = (
            firestore.Client().collection(f"stats_{os.environ.get('ENV')}").document(message.channel.name).get()
        )
        if not department_stats.exists:
            await message.channel.send(
                "There are no stats for this department yet.",
            )
            return

        task_config_data = get_task_config()
        user_doc = await check_registration_get_doc(message)
        current_task = await get_user_current_task(message)

        data = [["Task", "Average time", "Least time", "Your time"]]
        """
        Using for loops get tasks existing until current_task
        List stats for those tasks using stats doc and user's time using user_doc
        """
        for department in task_config_data["departments"]:
            if department["id"] == current_task["department_id"]:
                for objective in department["objectives"]:
                    for task in objective["tasks"]:
                        if task["id"] == current_task["task_id"]:
                            newline = "\n"
                            await message.channel.send(
                                f"Here's how you performed, <@{message.author.id}>!{newline}```{tabulate(data, headers='firstrow', tablefmt='fancy_grid')}```"
                            )
                            return
                        department_id = message.channel.name.replace("-", "_")
                        objective_id = objective["id"].replace("-", "_")
                        task_id = task["id"].replace("-", "_")
                        try:
                            average_time = department_stats.get(f"{objective_id}.{task_id}.average")
                            average_time = int(average_time)
                        except KeyError:
                            average_time = "N/A"

                        try:
                            least_time = department_stats.get(f"{objective_id}.{task_id}.least")
                            least_time = int(least_time)
                        except KeyError:
                            least_time = "N/A"

                        try:
                            user_time = user_doc.get(
                                f"stats_{os.environ.get('ENV')}.{department_id}.{objective_id}.{task_id}.time"
                            )
                            user_time = int(user_time)
                        except KeyError:
                            user_time = "N/A"

                        data.append(
                            [
                                task["name"],
                                f'{math.ceil(average_time/ 60 / 60 / 24)} day{"" if average_time <= 86400 and average_time > 0 else "s"}'
                                if isinstance(average_time, int)
                                else average_time,
                                f'{math.ceil(least_time / 60 / 60 / 24)} day{"" if least_time <= 86400 and least_time > 0 else "s"}'
                                if isinstance(least_time, int)
                                else least_time,
                                f'{math.ceil(user_time / 60 / 60 / 24)} day{"" if user_time <= 86400 and user_time > 0 else "s"}'
                                if isinstance(user_time, int)
                                else user_time,
                            ]
                        )
