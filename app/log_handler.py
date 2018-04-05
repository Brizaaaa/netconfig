import logging
from flask import session

# TODO remove this class and handler logging in the main app
# This enables us to use different log levels


class LogHandler(object):
    """Global log handler class."""

    def __init__(self, filename="netconfig.log", level="INFO"):
        """Initialize class."""
        self.logger = logging.getLogger(__name__)
        self.filename = filename
        self.level = level.upper()

        self.logger.setLevel(self.level)
        logging.basicConfig(filename=self.filename,
                            format='%(asctime)s %(levelname)s: %(message)s')

    def write_log(self, msg, user=None):
        """Write formatted 'msg' to logger."""
        # If a specific user is specific, log that user name
        if user:
            self.logger.info(user + ' - ' + msg)
        else:
            # Otherwise use currently logged in user
            try:
                # Log with currently logged in user
                self.logger.info(session['USER'] + ' - ' + msg)
            except (RuntimeError, KeyError):
                # If no user logged in, just log message only
                self.logger.info(msg)
