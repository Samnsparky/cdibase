"""Logic for sending email through the application.

@author: Sam Pottinger
@license: GNU GPL v2
"""

import threading

import flask.ext.mail as flask_mail


mail_lock = threading.Lock()


class MailKeeper:
    """Singleton to maintain SMTP mail client."""

    instance = None

    @classmethod
    def get_instance(cls):
        """Get a shared instance of this singleton.

        @return: Shared instance of the MailKeeper singleton.
        @rtype: MailKeeper
        """
        return cls.instance

    @classmethod
    def init_mail(cls, app):
        """Initialize the global MailKeeper singleton for the given app.

        @param app: The Flask app to initialize with.
        @type app: flask.Flask
        """
        cls.instance = MailKeeper(app)

    def __init__(self, app):
        """Create a new MailKeeper.

        @param app: The Flask app to create mailing capabilites for.
        @type app: flask.Flask
        """
        self.__mail = flask_mail.Mail(app)

    def get_mail_instance(self):
        """Get the underlying Flask-Mail client.

        @return: Flask-Mail SMTP client / facade.
        @rtype: flaskext.mail.Mail
        """
        return self.__mail


def init_mail(app):
    """Initialize the MailKeeper singleton to enable SMTP capabilities.

    Creates the system-wide MailKeeper singleton which allows the application to
    send email. This should be called once at the initialization of the Flask
    application.

    @param app: The flask application to initialize the MailKeeper with.
    @type app: flask.Flask
    """
    MailKeeper.init_mail(app)


def send_msg(message):
    """Send an email.

    @param message: The message to send.
    @type message: flaskext.mail.Message
    """
    with mail_lock:
        mail_instance = MailKeeper.get_instance().get_mail_instance()
        mail_instance.send(message)
