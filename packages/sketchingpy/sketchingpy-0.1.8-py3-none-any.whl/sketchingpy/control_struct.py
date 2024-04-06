"""Data structures to support inputs and controls.

License:
    BSD
"""

import typing


class Button:
    """Description of a key or button."""

    def __init__(self, name: str):
        """Create a new button record.

        Args:
            name: The name of the button.
        """
        self._name = name

    def get_name(self) -> str:
        """Get the name of this button.

        Returns:
            The name of the button.
        """
        return self._name


Buttons = typing.Iterable[Button]
KeyboardCallback = typing.Callable[[Button, 'Keyboard'], None]
MouseCallback = typing.Callable[[Button, 'Mouse'], None]


class Mouse:
    """Data structure describing a mouse."""

    def get_pointer_x(self):
        """Get the x coordinate of the mouse pointer.

        Get the current horizontal coordinate of the mouse pointer or, in the case of a touchscreen,
        the point of last touch input if available. Defaults to 0 if no mouse events have been seen.

        Returns:
            The horizontal coordinate of the mouse pointer.
        """
        raise NotImplementedError('Use implementor.')

    def get_pointer_y(self):
        """Get the y coordinate of the mouse pointer.

        Get the current vertical coordinate of the mouse pointer or, in the case of a touchscreen,
        the point of last touch input if available. Defaults to 0 if no mouse events have been seen.

        Returns:
            The vertical coordinate of the mouse pointer.
        """
        raise NotImplementedError('Use implementor.')

    def get_buttons_pressed(self) -> Buttons:
        """Information about the mouse buttons currently pressed.

        Get information about mouse buttons currently pressed.

        Returns:
            Collection of buttons currently pressed.
        """
        raise NotImplementedError('Use implementor.')

    def on_button_press(self, callback: MouseCallback):
        """Callback for when a mouse button is pressed.

        Register a callback for when a button is pressed, calling a function with the button and
        mouse. Will pass two arguments to that callback function: first a Button followed by a
        Mouse. Will unregister prior callbacks for on_button_press.

        Args:
            callback: The function to invoke when a mouse button or equivalent is pressed.
        """
        raise NotImplementedError('Use implementor.')

    def on_button_release(self, callback: MouseCallback):
        """Callback for when a mouse button is released.

        Register a callback for when a button is unpressed, calling a function with the button and
        mouse. Will pass two arguments to that callback function: first a Button followed by a
        Mouse. Will unregister prior callbacks for on_button_press.

        Args:
            callback: The function to invoke when a mouse button or equivalent is unpressed.
        """
        raise NotImplementedError('Use implementor.')


class Keyboard:
    """Data structure describing a keyboard."""

    def get_keys_pressed(self) -> Buttons:
        """Get a list of keys currently pressed.

        Get a list of keys as Buttons.

        Returns:
            Get list of buttons pressed.
        """
        raise NotImplementedError('Use implementor.')

    def on_key_press(self, callback: KeyboardCallback):
        """Callback for when a key is pressed.

        Register a callback for when a key is pressed, calling a function with the key and keyboard.
        Will pass two arguments to that callback function: first a Button followed by a Keyboard.
        Will unregister prior callbacks for on_key_press.

        Args:
            callback: The function to invoke when a key is pressed.
        """
        raise NotImplementedError('Use implementor.')

    def on_key_release(self, callback: KeyboardCallback):
        """Callback for when a key is released.

        Register a callback for when a key is unpressed, calling a function with the key and
        keyboard. Will pass two arguments to that callback function: first a Button followed by a
        Keyboard. Will unregister prior callbacks for on_key_release.

        Args:
            callback: The function to invoke when a key is released.
        """
        raise NotImplementedError('Use implementor.')
