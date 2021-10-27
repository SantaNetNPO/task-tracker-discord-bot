from datetime import datetime
import os
from google.cloud import firestore

from events.base_event import BaseEvent
from commands.task_utils import get_department_admins
import settings


class SlackerNotificationEvent(BaseEvent):
    def __init__(self):
        trigger_mode = "cron"
        kwargs = {"hour": 0}
        super().__init__(trigger_mode, kwargs)

    async def run(self, client):
        all_users = firestore.Client().collection(f"users_{os.environ.get('ENV')}").stream()
        santanet_guild = await client.fetch_guild(settings.GUILD_ID)

        department_admin_mapping = get_department_admins()
        for department in department_admin_mapping:
            department_users = filter(
                lambda user: any(
                    (current_task.get("department_id") == department) and (current_task.get("finished", False) is False)
                    for current_task in user.to_dict().get("current_task")
                ),
                all_users,
            )

            message = "**Slackers List:**\n"
            for user in department_users:
                for current_task in user.get("current_task"):
                    if current_task.get("department_id") == department:
                        discord_user = await santanet_guild.fetch_member(user.id)
                        message += f"{discord_user.display_name}: {(datetime.now() - datetime.fromtimestamp(current_task.get('task_started_time'))).days} days\n"

            for admin in department_admin_mapping[department]:
                admin_user = await client.fetch_user(admin)
                await admin_user.send(message)
