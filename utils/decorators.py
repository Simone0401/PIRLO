from functools import wraps
from flask import request, redirect, url_for
import os

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "supersegreto123")

# Decorator to ensure the user is an admin
# If the token in the cookies does not match the ADMIN_TOKEN, redirect to view containers
def admin_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.cookies.get("admin_token")
        if token != ADMIN_TOKEN:
            return redirect(url_for("containers.view_containers"))
        return f(*args, **kwargs)
    return wrapped
