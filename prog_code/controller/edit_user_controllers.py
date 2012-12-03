"""Logic for managing application users.

Logic for managing user and user access controlls for the application.

@author: Sam Pottinger
@license: GNU GPL v2
"""

import flask

from ..util import session_util
from ..util import user_util

from daxlabbase import app


@app.route("/edit_users")
@session_util.require_login(admin=True)
def edit_users():
    """Edit users with access to the application.

    @return: List of users with access to the application with links to add to,
        edit, and delete those accounts.
    @rtype: flask.Response
    """
    return flask.render_template(
        "edit_users.html",
        cur_page="edit_users",
        users=user_util.get_all_users(),
        **session_util.get_standard_template_values()
    )


@app.route("/edit_users/<email>/delete")
@session_util.require_login(admin=True)
def delete_user(email):
    """Controller to remove a user's access to this application.

    Controller that removes a record of a user account and ends that user's
    access to the application.

    @param email: The email of the user account to delete.
    @type email: str
    @return: Redirect
    @rtype: flask.Response
    """
    if not user_util.get_user(email):
        flask.session["error"] = "User \"%s\" could not be found." % email
        return flask.redirect("/edit_users")

    user_util.delete_user(email)
    flask.session["confirmation"] = "Account for %s deleted." % email
    return flask.redirect("/edit_users")


@app.route("/edit_users/_add", methods=["GET", "POST"])
@session_util.require_login(admin=True)
def add_user():
    """Controller to add a new user account to this application.

    @return: HTML form on GET and redirect on POST
    @rtype: flask.Response
    """
    request = flask.request
    if request.method == "GET":
        return flask.render_template(
            "edit_user.html",
            cur_page="edit_users",
            action_label="Create User",
            **session_util.get_standard_template_values()
        )

    elif request.method == "POST":
        email = request.form.get("email", "")

        if email == "":
            flask.session["error"] = "Email not provided. Please try again."
            return flask.redirect("/edit_users")

        if user_util.get_user(email):
            flask.session["error"] = "User \"%s\" already exists." % email
            return flask.redirect("/edit_users")

        user_util.create_new_user(
            email,
            request.form.get("can_enter_data", "") == "on",
            request.form.get("can_access_data", "") == "on",
            request.form.get("can_change_formats", "") == "on",
            request.form.get("can_admin", "") == "on"
        )
        flask.session["confirmation"] = "Account created for %s." % email
        return flask.redirect("/edit_users/_add")