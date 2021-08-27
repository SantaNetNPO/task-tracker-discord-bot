from commands.base_command import BaseCommand
import settings
from commands.firebase_utils import check_registration_get_doc
from commands.task_utils import get_task_config


class CurrentTask(BaseCommand):
    def __init__(self):
        description = "Shows the task you're currently on"
        params = []
        alternate_names = ["ct", "task"]
        super().__init__(description, params, alternate_names)

    async def handle(self, params, message, client):
        user_doc = await check_registration_get_doc(message)
        if user_doc:
            data = get_task_config()
            print(f"[DEBUG] {message.author.name}'s id: {message.author.id}")
            current_task = None

            # Find current_task details based on the message's channel.
            for item in user_doc.to_dict()["current_task"]:
                if item["department_id"] == "app-dev":  # message.channel.name:
                    current_task = item

            # If the message's channel is not a department channel, ask user to use this command in a department channel.
            if not current_task:
                await message.channel.send(
                    "You're not on the correct department channel, please trigger this command from the department whose task you want to check."
                )

            # Crawl through the tasks.yaml file to find the task's details.
            objective_found = False
            task_found = False
            for department in data["departments"]:
                if department["id"] == current_task["department_id"]:
                    for objective in department["objectives"]:
                        if objective["id"] == current_task["objective_id"]:
                            objective_found = True
                            for task in objective["tasks"]:
                                if task["id"] == current_task["task_id"]:
                                    subtask_no = current_task["subtask_no"]
                                    task_found = True
                                    task_name = task["name"]
                                    newline = "\n"
                                    check_mark = "\U00002705"
                                    pending_mark = "\U000023F3"
                                    await message.channel.send(
                                        f"Current task: **{task_name}**{newline}{newline.join(f'{check_mark if subtask_index < subtask_no else pending_mark} {subtask}' for subtask_index, subtask in enumerate(task['subtasks']))}"
                                    )
                                    return

            if not objective_found:
                await message.channel.send(
                    f"Objective not found, {settings.ADMIN_ROLE_MENTION} please look into this."
                )
            if not task_found:
                await message.channel.send(
                    f"Task not found, {settings.ADMIN_ROLE_MENTION} please look into this."
                )
