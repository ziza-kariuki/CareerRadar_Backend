def create_notification(user_id, message):
    return {
        "user_id": user_id,
        "message": message,
        "read": False
    }
