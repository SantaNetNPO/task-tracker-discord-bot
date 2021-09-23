from asyncio import sleep, TimeoutError
import time

import settings
from commands.current_task import CurrentTask
from commands.base_command import BaseCommand
from commands.task_utils import find_next_task, get_no_of_subtasks
from commands.firebase_utils import clear_user_cache, get_user_current_task, set_user_current_task


class CompleteTask(BaseCommand):
    def __init__(self):
        description = "Complete current task"
        params = []
        alternate_names = ["ct", "complete"]
        super().__init__(description, params, alternate_names)

    async def handle(self, params, message, client):
        """
        Get the current task properties based on channel
        Based on objective_id, task_id, subtask_no, incrementally increase
        each to get what the next task would be.
        Get approval from an admin to complete the task.
        """

        async with message.channel.typing():
            current_task = await get_user_current_task(message)
            if not current_task:
                "Fail gracefully since message response logic is handled in `get_user_current_task`"
                return

            no_of_subtasks = await get_no_of_subtasks(current_task, message)
            if not no_of_subtasks:
                "Fail gracefully since message response logic is handled in `get_no_of_subtasks`"
                return

        async with message.channel.typing():
            if no_of_subtasks - 1 > current_task["subtask_no"]:
                current_task["subtask_no"] += 1
                current_task["subtask_started_time"] = time.time()
                if await set_user_current_task(message, current_task):
                    await message.channel.send("Completed subtask! Posting the updated task message in a moment.")
                    clear_user_cache()
                    await CurrentTask().handle(params, message, client)
                    return

            approval_message = await message.channel.send(
                f"{settings.ADMIN_ROLE_MENTION}, please approve the completion of this task by reacting to this message with a 👍."
            )

        def check_admin_approval(reaction, user):
            user_is_admin = False
            for role in user.roles:
                if role.name == "admins":
                    user_is_admin = True
            return reaction.message.id == approval_message.id and user_is_admin and str(reaction.emoji) == "👍"

        try:
            await client.wait_for(
                "reaction_add",
                timeout=settings.REACTION_WAIT_TIMEOUT,
                check=check_admin_approval,
            )
        except TimeoutError:
            await approval_message.delete()
            try_again_message = await message.channel.send(
                "Task completion wasn't approved by the admins. Please try again later."
            )
            await sleep(3)
            await try_again_message.delete()
            await message.delete()
            return
        else:
            await approval_message.delete()

        async with message.channel.typing():
            next_objective_id, next_task_id = await find_next_task(current_task, message)
            if next_task_id is True:
                newline = "\n"
                await message.channel.send(
                    f"Congratulations on completing your task phase! You can start working for real for real now! :smile:{newline}{settings.ADMIN_ROLE_MENTION} take this up!"
                )
                return

            current_task["objective_id"] = next_objective_id
            current_task["task_id"] = next_task_id
            current_task["subtask_no"] = 0
            current_task["task_started_time"] = time.time()
            current_task["subtask_started_time"] = time.time()
            if await set_user_current_task(message, current_task):
                await message.channel.send("Completed task! Posting the new one in a moment.")
                clear_user_cache()
                await CurrentTask().handle(params, message, client)
                return
