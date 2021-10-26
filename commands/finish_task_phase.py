import os
from google.cloud import firestore

from commands.base_command import BaseCommand
import settings


class FinishTaskPhase(BaseCommand):
    def __init__(self):
        description = "Finish the task phase of a team member"
        params = ["@mention of member"]
        alternate_names = ["finish", "samapt"]
        super().__init__(description, params, alternate_names)

    async def handle(self, params, message, client):
        admin_roles = settings.ADMIN_ROLES
        sender_roles = [role.id for role in message.author.roles]
        is_sender_admin = any(role in admin_roles for role in sender_roles)

        if not is_sender_admin:
            await message.channel.send("You do not have permission to use this command.")
            return

        await message.channel.trigger_typing()

        task_phaser_id = params[0].strip("<@!>")
        task_phaser_doc = (
            firestore.Client().collection(f"users_{os.environ.get('ENV')}").document(str(task_phaser_id)).get()
        )

        if not task_phaser_doc.exists:
            await message.channel.send("Avoid @mentioning ghosts.")
            return

        task_phaser_data = task_phaser_doc.to_dict()
        task_phaser_current_tasks = task_phaser_data.get("current_task")
        for task in task_phaser_current_tasks:
            if task["department_id"] == str(message.channel.name):
                task_phaser_doc.reference.update({"current_task": firestore.ArrayRemove([task])})
                task["finished"] = True
                task_phaser_doc.reference.update({"current_task": firestore.ArrayUnion([task])})

                thumbs_up = "\U0001F44D"
                await message.channel.send(f"Done {thumbs_up}")
                return

        await message.channel.send(f"Member isn't registered for {message.channel.name}")
