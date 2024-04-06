"""Simple prompt dialog for local "app" renderer based in Pygame GUI.

Uses MIT licensed code from https://pygame-gui.readthedocs.io.

License:
    BSD
"""

import warnings
import typing

import pygame  # type: ignore
import pygame_gui.core  # type: ignore
import pygame_gui.core.interfaces  # type: ignore
import pygame_gui.elements  # type: ignore
import pygame_gui._constants  # type: ignore


class PygameGuiPrompt(pygame_gui.elements.UIWindow):
    """A prompt dialog for Pygame GUI.

    Simple dialog box which asks the user to confirm (offers a cancel option) with the option for
    the user to enter in text.
    """

    def __init__(self, rect: pygame.Rect, action_long_desc: str,
        manager=None, window_title: str = 'Prompt', action_short_name: str = 'pygame-gui.OK',
        blocking: bool = True, object_id=None, visible: int = 1,
        action_long_desc_text_kwargs: typing.Optional[typing.Dict[str, str]] = None):
        """Create a new prompt dialog.

        Args:
            rect: The location and bounds of the dialog.
            action_long_desc: Long string name description of the action the user is taking.
            manager: The manager in which to register this dialog.
            window_title: The title to display at the top of the dialog.
            action_short_name: Short name description of the action the user is taking in the UI.
            blocking: Flag indicating if the dialog should be blocking other UI interactions.
            object_id: The Pygame GUI ID to assign to the prompt.
            visible: Flag indicating if the prompt should start off being visible.
            action_long_desc_text_kwargs: Localization and long description strings.
        """

        if object_id is None:
            object_id = pygame_gui.core.ObjectID('#prompt_dialog', None)

        super().__init__(
            rect,
            manager,
            window_display_title=window_title,
            element_id='prompt_dialog',
            object_id=object_id,
            resizable=True,
            visible=visible
        )

        minimum_dimensions = (260, 200)
        if rect.width < minimum_dimensions[0] or rect.height < minimum_dimensions[1]:
            warn_string = ' '.join([
                'Initial size:',
                str(rect.size),
                'is less than minimum dimensions:',
                str(minimum_dimensions)
            ])
            warnings.warn(warn_string, UserWarning)
        self.set_minimum_dimensions(minimum_dimensions)

        self._cancel_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-10, -40, -1, 30),
            text='pygame-gui.Cancel',
            manager=self.ui_manager,
            container=self,
            object_id='#cancel_button',
            anchors={
                'left': 'right',
                'right': 'right',
                'top': 'bottom',
                'bottom': 'bottom'
            }
        )

        self._confirm_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-10, -40, -1, 30),
            text=action_short_name,
            manager=self.ui_manager,
            container=self,
            object_id='#confirm_button',
            anchors={
                'left': 'right',
                'right': 'right',
                'top': 'bottom',
                'bottom': 'bottom',
                'left_target': self._cancel_button,
                'right_target': self._cancel_button
            }
        )

        text_width = self.get_container().get_size()[0] - 10
        text_height = (self.get_container().get_size()[1] - 50) / 2 - 5
        self._prompt_text = pygame_gui.elements.UILabel(
            text=action_long_desc,
            relative_rect=pygame.Rect(5, 5, text_width, text_height),
            manager=self.ui_manager,
            container=self,
            anchors={
                'left': 'left',
                'right': 'right',
                'top': 'top',
                'bottom': 'bottom'
            },
            text_kwargs=action_long_desc_text_kwargs
        )

        self._input_box = pygame_gui.elements.UITextEntryBox(
            relative_rect=pygame.Rect(5, 5 + text_height + 5, text_width, text_height),
            manager=self.ui_manager,
            container=self,
            anchors={
                'left': 'left',
                'right': 'right',
                'top': 'top',
                'bottom': 'bottom'
            }
        )

        self._final_text: typing.Optional[str] = None

        self.set_blocking(blocking)

    def get_text(self) -> str:
        if self._final_text:
            return self._final_text
        else:
            return self._input_box.get_text()

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process dialog events.

        Args:
            event: The event to process.
        """
        consumed_event = super().process_event(event)

        button_pressed = event.type == pygame_gui._constants.UI_BUTTON_PRESSED
        if button_pressed:
            is_cancel = event.ui_element == self._cancel_button
            is_confirm = event.ui_element == self._confirm_button
        else:
            is_cancel = False
            is_confirm = False

        if button_pressed and is_cancel:
            self._final_text = ''
            self.kill()

        if button_pressed and is_confirm:
            # old event - to be removed in 0.8.0
            event_data = {
                'user_type': pygame_gui._constants.OldType(
                    pygame_gui._constants.UI_CONFIRMATION_DIALOG_CONFIRMED
                ),
                'ui_element': self,
                'ui_object_id': self.most_specific_combined_id
            }
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            # new event
            event_data = {
                'ui_element': self,
                'ui_object_id': self.most_specific_combined_id
            }
            pygame.event.post(pygame.event.Event(
                pygame_gui._constants.UI_CONFIRMATION_DIALOG_CONFIRMED,
                event_data
            ))
            self._final_text = self._input_box.get_text()
            self.kill()

        return consumed_event
