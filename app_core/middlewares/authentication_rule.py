from app_core.models.user import User, UserStatus

def authentication_rule(user: User) -> bool:
    return user is not None and user.status == UserStatus.ACTIVATED