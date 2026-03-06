
from functools import wraps
from flask import abort
from flask_login import current_user
# ensures that only valid users with active acc and correct role can access
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def check_role_and_execute(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            if not current_user.is_active:
                abort(403, description="Your account is deactivated.")
            return f(*args, **kwargs)
        return check_role_and_execute
    return wrapper
