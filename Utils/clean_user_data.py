def clean_user_data(user):
    fields=[
        "__v", "createdAt", "updatedAt"]
    for key in fields:
        user.pop(key, None)
    
    return user