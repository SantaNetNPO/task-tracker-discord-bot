from google.cloud import firestore


async def check_registration_get_doc(message):
    db = firestore.Client()
    doc_ref = db.collection("users").document(str(message.author.id))
    doc = doc_ref.get()
    if doc.exists:
        return doc
    else:
        await message.channel.send(
            "You are not registered. Please use `!register` to register."
        )
        return False
