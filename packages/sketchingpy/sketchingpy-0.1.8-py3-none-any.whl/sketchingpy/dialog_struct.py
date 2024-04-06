"""Utilities for showing simple dialog boxes..

License:
    BSD
"""

import typing


class DialogLayer:
    """Facade which allows for simple dialog boxes."""

    def show_alert(self, message: str, callback: typing.Optional[typing.Callable[[], None]] = None):
        """Show an alert dialog box.

        Args:
            callback: Method to invoke when the box closes.
            message: The string to show the user.
        """
        raise NotImplementedError('Use implementor.')

    def show_prompt(self, message: str,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        """Get a string input from the user.

        Args:
            message: The message to display to the user within the dialog.
            callback: Method to invoke when the box closes with a single string parameter provided
                by the user. Not invoked if cancelled.
        """
        raise NotImplementedError('Use implementor.')

    def get_file_save_location(self,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        """Get either the filename or full location for saving a file.

        Args:
            callback: Method to invoke when the box closes with single string parameter which is the
                filename or the path selected by the user. Not invoked if cancelled.
        """
        raise NotImplementedError('Use implementor.')

    def get_file_load_location(self,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        """Get either the filename or full location for opening a file.

        Args:
            callback: Method to invoke when the box closes with single string parameter which is the
                filename or the path selected by the user. Not invoked if cancelled.
        """
        raise NotImplementedError('Use implementor.')
