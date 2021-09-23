import os
from google.cloud import firestore

from commands.analytics_utils import update_subtask_stats, update_task_stats


previous_message_id = None
previous_user_doc = None


def clear_user_cache():
    """
    Clear the cache of the user
    """
    global previous_message_id
    global previous_user_doc
    previous_message_id = None
    previous_user_doc = None


async def check_registration_get_doc(message):
    """
    Query User data from Firebase
    Return from Cache if possible
    """
    global previous_message_id
    global previous_user_doc
    if message.id is previous_message_id:
        return previous_user_doc

    print("[Firebase]: Requesting User Data")

    db = firestore.Client()
    doc_ref = db.collection("users").document(str(message.author.id))
    doc = doc_ref.get()
    if doc.exists:
        previous_message_id = message.id
        previous_user_doc = doc
        return doc
    else:
        await message.channel.send("You are not registered. Please use `!register <department>` to register.")
        return False


async def get_user_current_task(message):
    """
    Get the current task parameters of the user where the department is chosen
    based on the channel in which the message was put up
    """
    user_doc = await check_registration_get_doc(message)
    if user_doc:
        for item in user_doc.to_dict()[f"current_task_{os.environ.get('ENV')}"]:
            if item["department_id"] == message.channel.name:
                return item
        # If the message's channel is not a department channel, ask user to use this command in a department channel.
        await message.channel.send(
            "You're not on the correct department channel, please trigger this command from the department whose task you want to check."
        )
        return False
    else:
        return False


async def set_user_current_task(message, updated_current_task):
    """
    Set the current task parameters of the user where the department is chosen
    based on the channel in which the message was put up

    Update statistics of the current task before updating the task parameters
    """
    user_doc = await check_registration_get_doc(message)
    current_task = await get_user_current_task(message)
    if user_doc:
        stats_doc_ref = (
            firestore.Client().collection(f"stats_{os.environ.get('ENV')}").document(current_task["department_id"])
        )
        stats_doc_dict = stats_doc_ref.get().to_dict()
        user_doc_dict_stats = user_doc.to_dict().get(f"stats_{os.environ.get('ENV')}", {})
        if updated_current_task["subtask_no"] == 0:
            stats_doc_dict, user_doc_dict_stats = update_task_stats(
                current_task,
                stats_doc_dict if stats_doc_dict is not None else {},
                user_doc_dict_stats,
            )

        stats_doc_dict, user_doc_dict_stats = update_subtask_stats(
            current_task,
            stats_doc_dict if stats_doc_dict is not None else {},
            user_doc_dict_stats,
        )

        stats_doc_ref.set(stats_doc_dict)
        user_doc.reference.update({f"stats_{os.environ.get('ENV')}": user_doc_dict_stats})

        user_doc.reference.update({f"current_task_{os.environ.get('ENV')}": firestore.ArrayRemove([current_task])})
        user_doc.reference.update(
            {f"current_task_{os.environ.get('ENV')}": firestore.ArrayUnion([updated_current_task])}
        )
        return True
    else:
        return False
