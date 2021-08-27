from commands.firebase_utils import check_registration_get_doc
from commands.base_command import BaseCommand
from commands.task_utils import get_departments, get_first_objective
from google.cloud import firestore


class Register(BaseCommand):
    def __init__(self):
        description = "Register for task phase"
        params = [f"department {str(get_departments())}"]
        alternate_names = []
        super().__init__(description, params, alternate_names)

    async def handle(self, params, message, client):
        user_exists = (
            firestore.Client()
            .collection("users")
            .document(str(message.author.id))
            .get()
            .exists
        )
        if not user_exists:
            firestore.Client().collection("users").document(str(message.author.id)).set(
                {}
            )

        user_doc = await check_registration_get_doc(message)

        department = params[0]
        departments = get_departments()
        if department not in departments:
            await message.channel.send(
                f"Invalid department, choose from {str(departments)}."
            )
            return
        first_objective = get_first_objective(department)

        for department_current_task in user_doc.to_dict().get("current_task") or []:
            if department_current_task["department_id"] == department:
                await message.channel.send(
                    f"You are already registered for '{department}'."
                )
                return
        firestore.Client().collection("users").document(str(message.author.id)).update(
            {
                "current_task": firestore.ArrayUnion(
                    [
                        {
                            "department_id": department,
                            "objective_id": first_objective["id"],
                            "task_id": first_objective["tasks"][0]["id"],
                            "subtask_no": 0,
                        }
                    ]
                )
            }
        )
        await message.channel.send(
            f"You're registered for {department}! Check out `!task` in the `{department}` channel!"
        )
