"""Pygame-based renderer for Sketchingpy.

License:
    BSD
"""

import contextlib
import copy
import math
import typing

import PIL.Image
import PIL.ImageFont

with contextlib.redirect_stdout(None):
    import pygame
    import pygame.draw
    import pygame.image
    import pygame.key
    import pygame.locals
    import pygame.mouse
    import pygame.time


ui_available = False
try:
    import pygame_gui  # type: ignore
    import pygame_gui.windows  # type: ignore
    import sketchingpy.pygame_prompt  # type: ignore
    ui_available = True
except:
    pass

import sketchingpy.abstracted
import sketchingpy.const
import sketchingpy.control_struct
import sketchingpy.data_struct
import sketchingpy.local_data_struct
import sketchingpy.pillow_util
import sketchingpy.sketch2d_keymap
import sketchingpy.state_struct
import sketchingpy.transform

DEFAULT_FPS = 20
MANUAL_OFFSET = True
OPTIONAL_SKETCH_CALLBACK = typing.Optional[typing.Callable[[sketchingpy.abstracted.Sketch], None]]


class Sketch2DApp(sketchingpy.abstracted.Sketch):
    """Create a new Pygame-based Sketch."""

    def __init__(self, width: int, height: int, title: typing.Optional[str] = None,
        loading_src: typing.Optional[str] = None):
        """Create a enw Pygame-based sketch.

        Args:
            width: The width of the sketch in pixels. This will be used for window width.
            height: The height of the sketch in pixels. This will be used for window height.
            title: Starting title for the application.
            loading_src: ID for loading screen. Ignored, reserved for future use.
        """
        super().__init__()

        # System params
        self._width = width
        self._height = height

        # Callbacks
        self._callback_step: OPTIONAL_SKETCH_CALLBACK = None
        self._callback_quit: OPTIONAL_SKETCH_CALLBACK = None

        # User configurable state
        self._state_frame_rate = DEFAULT_FPS

        # Buffers
        self._internal_surface = None
        self._output_surface = None
        self._buffers: typing.Dict[str, pygame.Surface] = {}

        # Internal state
        self._internal_pre_show_actions: typing.List[typing.Callable] = []
        self._internal_quit_requested = False
        self._internal_clock = pygame.time.Clock()
        self._transformer = sketchingpy.transform.Transformer()
        self._transformer_stack: typing.List[sketchingpy.transform.Transformer] = []
        self._dialog_layer: typing.Optional['AppDialogLayer'] = None

        # Inputs
        self._mouse = PygameMouse()
        self._keyboard = PygameKeyboard()

        # Internal struct
        self._struct_event_handlers = {
            pygame.KEYDOWN: lambda x: self._process_key_down(x),
            pygame.KEYUP: lambda x: self._process_key_up(x),
            pygame.MOUSEBUTTONDOWN: lambda x: self._process_mouse_down(x),
            pygame.MOUSEBUTTONUP: lambda x: self._process_mouse_up(x),
            pygame.locals.QUIT: lambda x: self._process_quit(x)
        }

        # Default window properties
        self.set_title('Sketchingpy Sketch' if title is None else title)

    ##########
    # Buffer #
    ##########

    def create_buffer(self, name: str, width: int, height: int,
        background: typing.Optional[str] = None):
        def execute():
            has_alpha = self._get_is_color_transparent(background)
            self._buffers[name] = self._make_shape_surface(
                pygame.Rect(0, 0, width, height),
                0,
                has_alpha=has_alpha
            )
            if not has_alpha:
                self._buffers[name].fill(pygame.Color(background))

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute)
        else:
            execute()

    def enter_buffer(self, name: str):
        def execute():
            self._internal_surface = self._buffers[name]

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute)
        else:
            execute()

    def exit_buffer(self):
        def execute():
            self._internal_surface = self._output_surface

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute)
        else:
            execute()

    def draw_buffer(self, x: float, y: float, name: str):
        def execute():
            target_surface = self._buffers[name]

            original_rect = target_surface.get_rect()
            rect = pygame.Rect(
                original_rect.x,
                original_rect.y,
                original_rect.width,
                original_rect.height
            )
            rect.left = x
            rect.top = y

            self._blit_with_transform(
                target_surface,
                rect.centerx,
                rect.centery,
                self._transformer.quick_copy()
            )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute)
        else:
            execute()

    ############
    # Controls #
    ############

    def get_keyboard(self) -> typing.Optional[sketchingpy.control_struct.Keyboard]:
        return self._keyboard

    def get_mouse(self) -> typing.Optional[sketchingpy.control_struct.Mouse]:
        return self._mouse

    ########
    # Data #
    ########

    def get_data_layer(self) -> typing.Optional[sketchingpy.data_struct.DataLayer]:
        return sketchingpy.local_data_struct.LocalDataLayer()

    ###########
    # Dialogs #
    ###########

    def get_dialog_layer(self) -> typing.Optional[sketchingpy.dialog_struct.DialogLayer]:
        if not ui_available:
            return None

        if self._dialog_layer is None:
            self._dialog_layer = AppDialogLayer(self)

        return self._dialog_layer

    ###########
    # Drawing #
    ###########

    def clear(self, color_hex: str):
        if self._internal_surface is None:
            self._internal_pre_show_actions.append(lambda: self.clear(color_hex))
            return

        self._internal_surface.fill(pygame.Color(color_hex))

    def draw_arc(self, x1: float, y1: float, x2: float, y2: float, a1: float,
        a2: float):
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        mode_native = state_machine.get_arc_mode_native()
        rect = self._build_rect_with_mode(x1, y1, x2, y2, mode_native)

        a1_rad = self._convert_to_radians(a1)
        a2_rad = self._convert_to_radians(a2)

        transformer = self._transformer.quick_copy()

        def execute_draw():
            pillow_util_image = sketchingpy.pillow_util.make_arc_image(
                rect.x,
                rect.y,
                rect.w,
                rect.h,
                a1_rad,
                a2_rad,
                stroke_enabled,
                fill_enabled,
                self._to_pillow_rgba(stroke_native) if stroke_enabled else None,
                self._to_pillow_rgba(fill_native) if fill_enabled else None,
                stroke_weight
            )

            native_image = self._convert_pillow_image(pillow_util_image.get_image())

            self._blit_with_transform(
                native_image,
                rect.centerx,
                rect.centery,
                transformer
            )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    def draw_ellipse(self, x1: float, y1: float, x2: float, y2: float):
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        mode_native = state_machine.get_ellipse_mode_native()
        rect = self._build_rect_with_mode(x1, y1, x2, y2, mode_native)

        transformer = self._transformer.quick_copy()

        def execute_draw():
            pillow_util_image = sketchingpy.pillow_util.make_ellipse_image(
                rect.x,
                rect.y,
                rect.w,
                rect.h,
                stroke_enabled,
                fill_enabled,
                self._to_pillow_rgba(stroke_native) if stroke_enabled else None,
                self._to_pillow_rgba(fill_native) if fill_enabled else None,
                stroke_weight
            )

            native_image = self._convert_pillow_image(pillow_util_image.get_image())

            self._blit_with_transform(
                native_image,
                rect.centerx,
                rect.centery,
                transformer
            )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    def draw_line(self, x1: float, y1: float, x2: float, y2: float):
        state_machine = self._get_current_state_machine()
        if not state_machine.get_stroke_enabled():
            return

        stroke_color = state_machine.get_stroke_native()
        stroke_weight = state_machine.get_stroke_weight_native()

        transformer = self._transformer.quick_copy()

        def execute_draw():
            min_x = min([x1, x2])
            max_x = max([x1, x2])
            width = max_x - min_x + 2 * stroke_weight

            min_y = min([y1, y2])
            max_y = max([y1, y2])
            height = max_y - min_y + 2 * stroke_weight

            rect = pygame.Rect(0, 0, width, height)
            target_surface = self._make_shape_surface(rect, stroke_weight)

            def adjust(target):
                return (
                    target[0] - min_x + stroke_weight,
                    target[1] - min_y + stroke_weight,
                )

            pygame.draw.line(
                target_surface,
                stroke_color,
                adjust((x1, y1)),
                adjust((x2, y2)),
                width=stroke_weight
            )

            center_x = (max_x + min_x) / 2
            center_y = (max_y + min_y) / 2
            self._blit_with_transform(target_surface, center_x, center_y, transformer)

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    def draw_rect(self, x1: float, y1: float, x2: float, y2: float):
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        mode_native = state_machine.get_rect_mode_native()
        rect = self._build_rect_with_mode(x1, y1, x2, y2, mode_native)

        transformer = self._transformer.quick_copy()

        def execute_draw():
            pillow_util_image = sketchingpy.pillow_util.make_rect_image(
                rect.x,
                rect.y,
                rect.w,
                rect.h,
                stroke_enabled,
                fill_enabled,
                self._to_pillow_rgba(stroke_native) if stroke_enabled else None,
                self._to_pillow_rgba(fill_native) if fill_enabled else None,
                stroke_weight
            )

            native_image = self._convert_pillow_image(pillow_util_image.get_image())

            self._blit_with_transform(
                native_image,
                rect.centerx,
                rect.centery,
                transformer
            )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    def draw_shape(self, shape: sketchingpy.shape_struct.Shape):
        if not shape.get_is_finished():
            raise RuntimeError('Finish your shape before drawing.')

        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        transformer = self._transformer.quick_copy()

        def execute_draw():
            pillow_util_image = sketchingpy.pillow_util.make_shape_image(
                shape,
                stroke_enabled,
                fill_enabled,
                self._to_pillow_rgba(stroke_native) if stroke_enabled else None,
                self._to_pillow_rgba(fill_native) if fill_enabled else None,
                stroke_weight
            )

            native_image = self._convert_pillow_image(pillow_util_image.get_image())

            min_x = shape.get_min_x()
            max_x = shape.get_max_x()
            center_x = (max_x + min_x) / 2

            min_y = shape.get_min_y()
            max_y = shape.get_max_y()
            center_y = (max_y + min_y) / 2

            self._blit_with_transform(
                native_image,
                center_x,
                center_y,
                transformer
            )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    def draw_text(self, x: float, y: float, content: str):
        content = str(content)
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        text_font = state_machine.get_text_font_native()
        fill_pillow = self._to_pillow_rgba(fill_native)
        stroke_pillow = self._to_pillow_rgba(stroke_native)

        align_info = state_machine.get_text_align_native()
        anchor_str = align_info.get_horizontal_align() + align_info.get_vertical_align()

        transformer = self._transformer.quick_copy()

        def execute_draw():
            pillow_util_image = sketchingpy.pillow_util.make_text_image(
                x,
                y,
                content,
                text_font,
                stroke_enabled,
                fill_enabled,
                stroke_pillow,
                fill_pillow,
                stroke_weight,
                anchor_str
            )

            native_image = self._convert_pillow_image(pillow_util_image.get_image())

            self._blit_with_transform(
                native_image,
                pillow_util_image.get_x() + pillow_util_image.get_width() / 2,
                pillow_util_image.get_y() + pillow_util_image.get_height() / 2,
                transformer
            )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    ##########
    # Events #
    ##########

    def on_step(self, callback: sketchingpy.abstracted.StepCallback):
        self._callback_step = callback

    def on_quit(self, callback: sketchingpy.abstracted.QuitCallback):
        self._callback_quit = callback

    #########
    # Image #
    #########

    def get_image(self, src: str) -> sketchingpy.abstracted.Image:
        return PygameImage(src)

    def draw_image(self, x: float, y: float, image: sketchingpy.abstracted.Image):
        if not image.get_is_loaded():
            return

        transformer = self._transformer.quick_copy()

        image_mode_native = self._get_current_state_machine().get_image_mode_native()

        def execute_draw():
            rect = self._build_rect_with_mode(
                x,
                y,
                image.get_width(),
                image.get_height(),
                image_mode_native
            )

            surface = image.get_native()
            self._blit_with_transform(surface, rect.centerx, rect.centery, transformer)

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
        else:
            execute_draw()

    def save_image(self, path: str):
        def execute_save():
            pygame.image.save(self._internal_surface, path)

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_save)
            self.show_and_quit()
        else:
            execute_save()

    #########
    # State #
    #########

    def push_transform(self):
        self._transformer_stack.append(copy.deepcopy(self._transformer))

    def pop_transform(self):
        if len(self._transformer_stack) == 0:
            raise RuntimeError('Transformation stack empty.')

        self._transformer = self._transformer_stack.pop()

    ##########
    # System #
    ##########

    def get_native(self):
        if self._internal_surface is None:
            raise RuntimeError('Need to show sketch first before surface is available.')

        return self._internal_surface

    def set_fps(self, rate: int):
        self._state_frame_rate = rate

    def set_title(self, title: str):
        def execute():
            pygame.display.set_caption(title)

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute)
        else:
            execute()

    def quit(self):
        self._internal_quit_requested = True

    def show(self, ax=None):
        self._show_internal(ax=ax, quit_immediately=False)

    def show_and_quit(self, ax=None):
        self._show_internal(ax=ax, quit_immediately=True)

    #############
    # Transform #
    #############

    def translate(self, x: float, y: float):
        self._transformer.translate(x, y)

    def rotate(self, angle_mirror: float):
        angle = -1 * angle_mirror
        angle_rad = self._convert_to_radians(angle)
        self._transformer.rotate(angle_rad)

    def scale(self, scale: float):
        self._transformer.scale(scale)

    ###########
    # Support #
    ###########

    def _get_window_size(self) -> typing.Tuple[int, int]:
        return (self._width, self._height)

    def _show_internal(self, ax=None, quit_immediately=False):
        pygame.init()
        self._internal_surface = pygame.display.set_mode((self._width, self._height))
        self._output_surface = self._internal_surface

        for action in self._internal_pre_show_actions:
            action()

        self._inner_loop(quit_immediately=quit_immediately)

    def _inner_loop(self, quit_immediately=False):
        clock = pygame.time.Clock()

        while not self._internal_quit_requested:
            time_delta = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                self._process_event(event)
                if self._dialog_layer:
                    self._dialog_layer.get_manager().process_events(event)
                    dialog = self._dialog_layer.get_dialog()
                    try:
                        if dialog is not None and event.ui_element == dialog:
                            self._dialog_layer.report_close(event)
                    except AttributeError:
                        pass

            if self._dialog_layer:
                self._dialog_layer.get_manager().update(time_delta)

            if self._callback_step is not None:
                self._callback_step(self)

            if self._dialog_layer:
                self._dialog_layer.get_manager().draw_ui(self._internal_surface)

            pygame.display.update()
            self._internal_clock.tick(self._state_frame_rate)

            if quit_immediately:
                self._internal_quit_requested = True

        if self._callback_quit is not None:
            self._callback_quit(self)

    def _process_event(self, event):
        if event.type not in self._struct_event_handlers:
            return

        self._struct_event_handlers[event.type](event)

    def _process_quit(self, event):
        self._internal_quit_requested = True

    def _process_mouse_down(self, event):
        self._mouse.report_mouse_down(event)

    def _process_mouse_up(self, event):
        self._mouse.report_mouse_up(event)

    def _process_key_down(self, event):
        self._keyboard.report_key_down(event)

    def _process_key_up(self, event):
        self._keyboard.report_key_up(event)

    def _create_state_machine(self) -> sketchingpy.state_struct.SketchStateMachine:
        return PygameSketchStateMachine()

    def _make_shape_surface(self, rect: pygame.Rect, stroke_weight: float,
        has_alpha: bool = True) -> pygame.Surface:
        if has_alpha:
            return pygame.Surface((rect.w + stroke_weight, rect.h + stroke_weight), pygame.SRCALPHA)
        else:
            return pygame.Surface((rect.w + stroke_weight, rect.h + stroke_weight))

    def _zero_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(0, 0, rect.w, rect.h)

    def _build_rect_with_mode(self, x1: float, y1: float, x2: float, y2: float,
        native_mode: int) -> pygame.Rect:
        if native_mode == sketchingpy.const.CENTER:
            start_x = x1 - math.floor(x2 / 2)
            start_y = y1 - math.floor(y2 / 2)
            width = x2
            height = y2
        elif native_mode == sketchingpy.const.RADIUS:
            start_x = x1 - x2
            start_y = y1 - y2
            width = x2 * 2
            height = y2 * 2
        elif native_mode == sketchingpy.const.CORNER:
            start_x = x1
            start_y = y1
            width = x2
            height = y2
        elif native_mode == sketchingpy.const.CORNERS:
            (x1, y1, x2, y2) = sketchingpy.abstracted.reorder_coords(x1, y1, x2, y2)
            start_x = x1
            start_y = y1
            width = x2 - x1
            height = y2 - y1
        else:
            raise RuntimeError('Unknown mode: ' + str(native_mode))

        return pygame.Rect(start_x, start_y, width, height)

    def _draw_primitive(self, x1: float, y1: float, x2: float, y2: float,
        mode: str, native_mode, draw_method):
        state_machine = self._get_current_state_machine()
        has_fill = state_machine.get_fill_enabled()
        fill_color = state_machine.get_fill_native()
        has_stroke = state_machine.get_stroke_enabled()
        stroke_color = state_machine.get_stroke_native()
        rect = self._build_rect_with_mode(x1, y1, x2, y2, native_mode)
        stroke_weight = state_machine.get_stroke_weight_native()

        transformer = self._transformer.quick_copy()

        def execute_draw_piece(color, strategy):
            target_surface = self._make_shape_surface(rect, stroke_weight)
            rect_adj = self._zero_rect(rect)

            strategy(target_surface, rect_adj)

            self._blit_with_transform(
                target_surface,
                rect.centerx,
                rect.centery,
                transformer
            )

        def execute_draw():
            if has_fill:
                execute_draw_piece(
                    fill_color,
                    lambda surface, rect: draw_method(
                        surface,
                        fill_color,
                        self._offset_fill_weight(rect, stroke_weight),
                        0
                    )
                )

            if has_stroke:
                execute_draw_piece(
                    stroke_color,
                    lambda surface, rect: draw_method(
                        surface,
                        stroke_color,
                        self._offset_stroke_weight(rect, stroke_weight),
                        stroke_weight
                    )
                )

        if self._internal_surface is None:
            self._internal_pre_show_actions.append(execute_draw)
            return
        else:
            execute_draw()

    def _to_pillow_rgba(self, target: pygame.Color):
        return (target.r, target.g, target.b, target.a)

    def _convert_pillow_image(self, target: PIL.Image.Image) -> pygame.Surface:
        return pygame.image.fromstring(
            target.tobytes(),
            target.size,
            target.mode  # type: ignore
        ).convert_alpha()

    def _blit_with_transform(self, surface: pygame.Surface, x: float, y: float,
        transformer: sketchingpy.transform.Transformer):
        start_rect = surface.get_rect()
        start_rect.centerx = x  # type: ignore
        start_rect.centery = y  # type: ignore

        transformed_center = transformer.transform(
            start_rect.centerx,
            start_rect.centery
        )

        has_scale = transformed_center.get_scale() != 1
        has_rotation = transformed_center.get_rotation() != 0
        has_content_transform = has_scale or has_rotation
        if has_content_transform:
            angle = transformed_center.get_rotation()
            angle_transform = math.degrees(angle)
            scale = transformed_center.get_scale()
            surface = pygame.transform.rotozoom(surface, angle_transform, scale)
            end_rect = surface.get_rect()
        else:
            end_rect = start_rect

        end_rect.centerx = transformed_center.get_x()  # type: ignore
        end_rect.centery = transformed_center.get_y()  # type: ignore

        assert self._internal_surface is not None
        self._internal_surface.blit(surface, (end_rect.x, end_rect.y))


class PygameSketchStateMachine(sketchingpy.state_struct.SketchStateMachine):
    """Implementation of SketchStateMachine for Pygame types."""

    def __init__(self):
        """Create a new state machine for Pygame-based sketches."""
        super().__init__()
        self._fill_native = pygame.Color(super().get_fill())
        self._stroke_native = pygame.Color(super().get_stroke())
        self._font_cache = {}
        self._text_align_native = self._transform_text_align(super().get_text_align_native())

    def set_fill(self, fill: str):
        super().set_fill(fill)
        self._fill_native = pygame.Color(super().get_fill())

    def get_fill_native(self):
        return self._fill_native

    def set_stroke(self, stroke: str):
        super().set_stroke(stroke)
        self._stroke_native = pygame.Color(super().get_stroke())

    def get_stroke_native(self):
        return self._stroke_native

    def get_text_font_native(self):
        font = self.get_text_font()
        key = '%s.%d' % (font.get_identifier(), font.get_size())

        if key not in self._font_cache:
            new_font = PIL.ImageFont.truetype(font.get_identifier(), font.get_size())
            self._font_cache[key] = new_font

        return self._font_cache[key]

    def set_text_align(self, text_align: sketchingpy.state_struct.TextAlign):
        super().set_text_align(text_align)
        self._text_align_native = self._transform_text_align(super().get_text_align_native())

    def get_text_align_native(self):
        return self._text_align_native

    def _transform_text_align(self,
        text_align: sketchingpy.state_struct.TextAlign) -> sketchingpy.state_struct.TextAlign:

        HORIZONTAL_ALIGNS = {
            sketchingpy.const.LEFT: 'l',
            sketchingpy.const.CENTER: 'm',
            sketchingpy.const.RIGHT: 'r'
        }

        VERTICAL_ALIGNS = {
            sketchingpy.const.TOP: 't',
            sketchingpy.const.CENTER: 'm',
            sketchingpy.const.BASELINE: 's',
            sketchingpy.const.BOTTOM: 'b'
        }

        return sketchingpy.state_struct.TextAlign(
            HORIZONTAL_ALIGNS[text_align.get_horizontal_align()],
            VERTICAL_ALIGNS[text_align.get_vertical_align()]
        )


class PygameImage(sketchingpy.abstracted.Image):
    """Strategy implementation for Pygame images."""

    def __init__(self, src: str):
        """Create a new image.

        Args:
            src: Path to the image.
        """
        super().__init__(src)
        self._native = pygame.image.load(self.get_src())
        self._converted = False

    def get_width(self) -> float:
        return self._native.get_rect().width

    def get_height(self) -> float:
        return self._native.get_rect().height

    def resize(self, width: float, height: float):
        self._native = pygame.transform.scale(self._native, (width, height))

    def get_native(self):
        if not self._converted:
            self._native.convert_alpha()

        return self._native

    def get_is_loaded(self):
        return True


class PygameMouse(sketchingpy.control_struct.Mouse):
    """Strategy implementation for Pygame-based mouse access."""

    def __init__(self):
        """Create a new mouse strategy using Pygame."""
        super().__init__()
        self._press_callback = None
        self._release_callback = None

    def get_pointer_x(self):
        return pygame.mouse.get_pos()[0]

    def get_pointer_y(self):
        return pygame.mouse.get_pos()[1]

    def get_buttons_pressed(self) -> sketchingpy.control_struct.Buttons:
        is_left_pressed = pygame.mouse.get_pressed()[0]
        is_right_pressed = pygame.mouse.get_pressed()[2]
        buttons_clicked = []

        if is_left_pressed:
            buttons_clicked.append(sketchingpy.const.MOUSE_LEFT_BUTTON)

        if is_right_pressed:
            buttons_clicked.append(sketchingpy.const.MOUSE_RIGHT_BUTTON)

        return map(lambda x: sketchingpy.control_struct.Button(x), buttons_clicked)

    def on_button_press(self, callback: sketchingpy.control_struct.MouseCallback):
        self._press_callback = callback

    def on_button_release(self, callback: sketchingpy.control_struct.MouseCallback):
        self._release_callback = callback

    def report_mouse_down(self, event):
        if self._press_callback is None:
            return

        if event.button == 1:
            button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_LEFT_BUTTON)
            self._press_callback(button)
        elif event.button == 3:
            button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_RIGHT_BUTTON)
            self._press_callback(button)

    def report_mouse_up(self, event):
        if self._release_callback is None:
            return

        if event.button == 1:
            button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_LEFT_BUTTON)
            self._release_callback(button)
        elif event.button == 3:
            button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_RIGHT_BUTTON)
            self._release_callback(button)


class PygameKeyboard(sketchingpy.control_struct.Keyboard):
    """Strategy implementation for Pygame-based keyboard access."""

    def __init__(self):
        """Create a new keyboard strategy using Pygame."""
        super().__init__()
        self._pressed = set()
        self._press_callback = None
        self._release_callback = None

    def get_keys_pressed(self) -> sketchingpy.control_struct.Buttons:
        return map(lambda x: sketchingpy.control_struct.Button(x), self._pressed)

    def on_key_press(self, callback: sketchingpy.control_struct.KeyboardCallback):
        self._press_callback = callback

    def on_key_release(self, callback: sketchingpy.control_struct.KeyboardCallback):
        self._release_callback = callback

    def report_key_down(self, event):
        mapped = sketchingpy.sketch2d_keymap.KEY_MAP.get(event.key, None)

        if mapped is None:
            return

        self._pressed.add(mapped)

        if self._press_callback is not None:
            button = sketchingpy.control_struct.Button(mapped)
            self._press_callback(button)

    def report_key_up(self, event):
        mapped = sketchingpy.sketch2d_keymap.KEY_MAP.get(event.key, None)

        if mapped is None:
            return

        self._pressed.remove(mapped)

        if self._release_callback is not None:
            button = sketchingpy.control_struct.Button(mapped)
            self._release_callback(button)


class AppDialogLayer(sketchingpy.dialog_struct.DialogLayer):
    """Dialog / simple UI layer for local apps."""

    def __init__(self, sketch: Sketch2DApp):
        """"Initialize tkinter but hide the root window."""
        self._sketch = sketch
        self._sketch_size = self._sketch._get_window_size()
        self._manager = pygame_gui.UIManager(self._sketch_size)
        self._callback = None  # type: ignore
        self._dialog = None  # type: ignore

    def get_manager(self):
        return self._manager

    def get_dialog(self):
        return self._dialog

    def report_close(self, event):
        if self._callback:
            self._callback(event)

    def show_alert(self, message: str, callback: typing.Optional[typing.Callable[[], None]] = None):
        self._dispose_dialog()
        self._dialog = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(
                self._sketch_size[0] / 2 - 150,
                self._sketch_size[1] / 2 - 150,
                300,
                300
            ),
            html_message=message,
            manager=self._manager
        )

        def outer_callback(event):
            if event.type == pygame_gui._constants.UI_BUTTON_PRESSED and callback:
                callback()

        self._callback = outer_callback  # type: ignore

    def show_prompt(self, message: str,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        self._dialog = sketchingpy.pygame_prompt.PygameGuiPrompt(  # type: ignore
            rect=pygame.Rect(
                self._sketch_size[0] / 2 - 150,
                self._sketch_size[1] / 2 - 150,
                300,
                300
            ),
            action_long_desc=message,
            manager=self._manager,
            window_title='Prompt'
        )

        def outer_callback(event):
            if event.type == pygame_gui._constants.UI_CONFIRMATION_DIALOG_CONFIRMED:
                callback(str(self._dialog.get_text()))

        self._callback = outer_callback  # type: ignore

    def get_file_save_location(self,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        self._dispose_dialog()
        self._dialog = pygame_gui.windows.ui_file_dialog.UIFileDialog(
            rect=pygame.Rect(
                self._sketch_size[0] / 2 - 150,
                self._sketch_size[1] / 2 - 150,
                300,
                300
            ),
            manager=self._manager,
            allow_existing_files_only=False,
            window_title='Save'
        )
        self._callback = self._make_file_dialog_callback(callback)  # type: ignore

    def get_file_load_location(self,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        self._dispose_dialog()
        self._dialog = pygame_gui.windows.ui_file_dialog.UIFileDialog(
            rect=pygame.Rect(
                self._sketch_size[0] / 2 - 150,
                self._sketch_size[1] / 2 - 150,
                300,
                300
            ),
            manager=self._manager,
            allow_existing_files_only=False,
            window_title='Load'
        )
        self._callback = self._make_file_dialog_callback(callback)  # type: ignore

    def _make_file_dialog_callback(self, inner_callback):
        def callback(event):
            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                inner_callback(str(self._dialog.current_file_path))

        return callback

    def _dispose_dialog(self):
        if self._dialog:
            self._dialog.kill()
