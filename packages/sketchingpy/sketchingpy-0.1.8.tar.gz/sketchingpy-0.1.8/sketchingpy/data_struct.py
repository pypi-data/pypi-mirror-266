"""Data structures to support data access (file system, network, browser).

License:
    BSD
"""

import typing

Columns = typing.Iterable[str]
Records = typing.Iterable[typing.Dict]


class DataLayer:
    """Facade (strategy) for access to data."""

    def get_csv(self, path: str) -> Records:
        """Load a CSV file as a list of dictionaries.

        Load a CSV file and parse it as a list where each row after the "header row" becomes a
        dictionary.

        Args:
            path: The location at which the CSV file can be found.

        Returns:
            List of dictionary.
        """
        raise NotImplementedError('Use implementor.')

    def write_csv(self, records: Records, columns: Columns, path: str):
        """Write a list of dictionaries as a CSV file.

        Write a CSV file with header row, saving it to local file system or offering it as a
        download in the browser.

        Args:
            records: List of dictionaries to be written.
            columns: Ordered list of columns to include in the CSV file.
            path: The location at which the file should be written.
        """
        raise NotImplementedError('Use implementor.')

    def get_json(self, path: str):
        """Read a JSON file.

        Read a JSON file either from local file system or the network.

        Args:
            path: The location at which the JSON file can be found.

        Returns:
            Loaded JSON content.
        """
        raise NotImplementedError('Use implementor.')

    def write_json(self, target, path: str):
        """Write a JSON file.

        Write a JSON file, saving it to local file system or offering it as a download in the
        browser.

        Args:
            target: The value to write as JSON.
            path: The location at which the file should be written.
        """
        raise NotImplementedError('Use implementor.')

    def get_text(self, path: str):
        """Read a text file.

        Read a text file either from local file system or the network.

        Args:
            path: The location where the file can be found.

        Returns:
            Loaded content as a string.
        """
        raise NotImplementedError('Use implementor.')

    def write_text(self, target: str, path: str):
        """Write a text file.

        Write a text file, saving it to local file system or offering it as a download in the
        browser.

        Args:
            target: The contents to write.
            path: The location at which the file should be written.
        """
        raise NotImplementedError('Use implementor.')
