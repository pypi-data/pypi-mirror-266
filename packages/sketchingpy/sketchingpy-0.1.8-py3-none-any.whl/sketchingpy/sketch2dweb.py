"""HTML5 Canvas-based renderer for Sketchingpy.

License:
    BSD
"""

import csv
import io
import json
import os.path
import time
import typing
import urllib.parse

has_js = False
try:
    import js  # type: ignore
    import pyodide.ffi  # type: ignore
    import pyodide.http  # type: ignore
    import pyscript  # type: ignore
    has_js = True
except:
    pass

import sketchingpy.abstracted
import sketchingpy.const
import sketchingpy.control_struct
import sketchingpy.data_struct
import sketchingpy.state_struct

DEFAULT_FPS = 20

KEY_MAP = {
    'ArrowLeft': sketchingpy.const.KEYBOARD_LEFT_BUTTON,
    'ArrowUp': sketchingpy.const.KEYBOARD_UP_BUTTON,
    'ArrowRight': sketchingpy.const.KEYBOARD_RIGHT_BUTTON,
    'ArrowDown': sketchingpy.const.KEYBOARD_DOWN_BUTTON,
    ' ': sketchingpy.const.KEYBOARD_SPACE_BUTTON,
    'Control': sketchingpy.const.KEYBOARD_CTRL_BUTTON,
    'Alt': sketchingpy.const.KEYBOARD_ALT_BUTTON,
    'Shift': sketchingpy.const.KEYBOARD_SHIFT_BUTTON,
    'Tab': sketchingpy.const.KEYBOARD_TAB_BUTTON,
    'Home': sketchingpy.const.KEYBOARD_HOME_BUTTON,
    'End': sketchingpy.const.KEYBOARD_END_BUTTON,
    'Enter': sketchingpy.const.KEYBOARD_RETURN_BUTTON,
    'Backspace': sketchingpy.const.KEYBOARD_BACKSPACE_BUTTON,
    'null': None
}

OPTIONAL_SKETCH_CALLBACK = typing.Optional[typing.Callable[[sketchingpy.abstracted.Sketch], None]]


class CanvasRegionEllipse:
    """Description of a region of a canvas expressed as an ellipse."""

    def __init__(self, x: float, y: float, radius_x: float, radius_y: float):
        """Create a new elliptical region record.

        Args:
            x: The center x coordinate of the region.
            y: The center y coordinate of the region.
            radius_x: The horizontal radius of the region.
            radius_y: The vertical radius of the region.
        """
        self._x = x
        self._y = y
        self._radius_x = radius_x
        self._radius_y = radius_y

    def get_x(self) -> float:
        """Get the center horizontal coordinate of this region.

        Returns:
            The center x coordinate of the region.
        """
        return self._x

    def get_y(self) -> float:
        """Get the center vertical coordinate of this region.

        Returns:
            The center y coordinate of the region.
        """
        return self._y

    def get_radius_x(self) -> float:
        """Get the horizontal size of this region.

        Returns:
            The horizontal radius of the region.
        """
        return self._radius_x

    def get_radius_y(self) -> float:
        """Get the vertical size of this region.

        Returns:
            The vertical radius of the region.
        """
        return self._radius_y


class CanvasRegionRect:
    """Description of a region of a canvas expressed as a rectangle."""

    def __init__(self, x: float, y: float, width: float, height: float):
        """Create a new rectangular region record.

        Args:
            x: The center x coordinate of the region.
            y: The center y coordinate of the region.
            radius_x: The horizontal size of the region.
            radius_y: The vertical size of the region.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    def get_x(self) -> float:
        """Get the start horizontal coordinate of this region.

        Returns:
            The left x coordinate of the region.
        """
        return self._x

    def get_y(self) -> float:
        """Get the start vertical coordinate of this region.

        Returns:
            The top y coordinate of the region.
        """
        return self._y

    def get_width(self) -> float:
        """Get the horizontal size of this region.

        Returns:
            The horizontal width of the region.
        """
        return self._width

    def get_height(self) -> float:
        """Get the vertical size of this region.

        Returns:
            The vertical height of the region.
        """
        return self._height


class WebBuffer:
    """Structure for an offscreen buffer."""

    def __init__(self, canvas, context, width: int, height: int):
        """Create a new offscreen record.

        Args:
            canvas: The offscreen canvas element.
            context: The 2D drawing context.
            width: The horizontal size of the buffer in pixels.
            height: The vertical size of the buffer in pixels.
        """
        self._canvas = canvas
        self._context = context
        self._width = width
        self._height = height

    def get_element(self):
        """Get the offscreen canvas object.

        Returns:
            The offscreen canvas element.
        """
        return self._canvas

    def get_context(self):
        """Get the drawing context compatiable with the main canvas.

        Returns:
            The 2D drawing context.
        """
        return self._context

    def get_width(self) -> int:
        """Get the horizontal size of the buffer in pixels.

        Returns:
            Width of the offscreen canvas.
        """
        return self._width

    def get_height(self) -> int:
        """Get the vertical size of the buffer in pixels.

        Returns:
            Height of the offscreen canvas.
        """
        return self._height


class Sketch2DWeb(sketchingpy.abstracted.Sketch):
    """Sketch renderer for web / HTML5."""

    def __init__(self, width: float, height: float, element_id: str = 'sketch-canvas',
        loading_id: typing.Optional[str] = 'sketch-load-message'):
        """Create a new HTML5 Canvas-based sketch.

        Args:
            width: The horizontal size of the sketch in pixels. Will update the HTML5 element.
            height: The vertical size of the sketch in pixels. Will update the HTML5 element.
            element_id: The ID (HTML) of the canvas into which this sketch should be drawn.
            loading_id: The ID (HTML) of the loading message to hide upon showing the sketch.
        """
        super().__init__()

        if not has_js:
            raise RuntimeError('Cannot access JS / pyodide.')

        # Save elements required for running the canvas
        self._element_id = element_id
        self._element = js.document.getElementById(element_id)
        self._element.width = width
        self._element.height = height
        self._element.style.display = 'none'
        self._context = self._element.getContext('2d')
        self._last_render = None

        self._loading_id = loading_id
        self._loading_element = js.document.getElementById(loading_id)

        # Internal only elements
        self._internal_loop_callback = None
        self._internal_mouse_x = 0
        self._internal_mouse_y = 0
        self._internal_pre_show_actions: typing.List[typing.Callable] = []

        # Buffers
        self._buffers: typing.Dict[str, WebBuffer] = {}
        self._base_context = self._context
        self._base_element = self._element
        self._width = self._element.width
        self._height = self._element.height

        # User configurable state
        self._state_frame_rate = DEFAULT_FPS
        self._stopped = False

        # Callback
        self._callback_step: OPTIONAL_SKETCH_CALLBACK = None
        self._callback_quit: OPTIONAL_SKETCH_CALLBACK = None

        # Control
        self._keyboard = PyscriptKeyboard(self._element)
        self._mouse = PyscriptMouse(self._element)

    ##########
    # Buffer #
    ##########

    def create_buffer(self, name: str, width: int, height: int,
        background: typing.Optional[str] = None):
        canvas = js.window.OffscreenCanvas.new(width, height)
        context = canvas.getContext('2d')
        self._buffers[name] = WebBuffer(canvas, context, width, height)
        if background is not None:
            context.clearRect(0, 0, self._width, self._height)
            context.fillStyle = background
            context.fillRect(0, 0, self._width, self._height)

    def enter_buffer(self, name: str):
        web_buffer = self._buffers[name]
        self._context = web_buffer.get_context()
        self._element = web_buffer.get_element()
        self._width = web_buffer.get_width()
        self._height = web_buffer.get_height()

    def exit_buffer(self):
        self._context = self._base_context
        self._element = self._base_element
        self._width = self._base_element.width
        self._height = self._base_element.height

    def draw_buffer(self, x: float, y: float, name: str):
        web_buffer = self._buffers[name]
        self._context.drawImage(web_buffer.get_element(), x, y)

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
        return WebDataLayer()

    ###########
    # Dialogs #
    ###########

    def get_dialog_layer(self) -> typing.Optional[sketchingpy.dialog_struct.DialogLayer]:
        return WebDialogLayer(self)

    ###########
    # Drawing #
    ###########

    def clear(self, color: str):
        self._context.clearRect(0, 0, self._width, self._height)
        self._context.fillStyle = color
        self._context.fillRect(0, 0, self._width, self._height)

    def draw_arc(self, x1: float, y1: float, x2: float, y2: float, a1: float, a2: float):
        self._load_draw_params()

        a1_rad = self._convert_to_radians(a1) - js.Math.PI / 2
        a2_rad = self._convert_to_radians(a2) - js.Math.PI / 2

        current_machine = self._get_current_state_machine()
        mode_native = current_machine.get_arc_mode_native()
        mode_str = current_machine.get_arc_mode()

        self._draw_arc_rad(x1, y1, x2, y2, a1_rad, a2_rad, mode_native, mode_str)

    def draw_ellipse(self, x1: float, y1: float, x2: float, y2: float):
        current_machine = self._get_current_state_machine()
        mode_native = current_machine.get_ellipse_mode_native()
        mode_str = current_machine.get_ellipse_mode()

        self._draw_arc_rad(x1, y1, x2, y2, 0, 2 * js.Math.PI, mode_native, mode_str)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float):
        current_machine = self._get_current_state_machine()
        if not current_machine.get_stroke_enabled():
            return

        self._load_draw_params()

        self._context.beginPath()
        self._context.moveTo(x1, y1)
        self._context.lineTo(x2, y2)
        self._context.stroke()

    def draw_rect(self, x1: float, y1: float, x2: float, y2: float):
        self._load_draw_params()

        current_machine = self._get_current_state_machine()
        native_mode = current_machine.get_rect_mode_native()
        mode_str = current_machine.get_rect_mode_native()

        region = self._get_canvas_region_rect_like(x1, y1, x2, y2, native_mode, mode_str)

        self._context.beginPath()
        self._context.rect(region.get_x(), region.get_y(), region.get_width(), region.get_height())

        if current_machine.get_fill_enabled():
            self._context.fill()

        if current_machine.get_stroke_enabled():
            self._context.stroke()

    def draw_shape(self, shape: sketchingpy.shape_struct.Shape):
        current_machine = self._get_current_state_machine()

        self._load_draw_params()

        self._context.beginPath()
        self._context.moveTo(shape.get_start_x(), shape.get_start_y())

        for segment in shape.get_segments():
            strategy = segment.get_strategy()
            if strategy == 'straight':
                self._context.lineTo(segment.get_destination_x(), segment.get_destination_y())
            elif strategy == 'bezier':
                self._context.bezierCurveTo(
                    segment.get_control_x1(),
                    segment.get_control_y1(),
                    segment.get_control_x2(),
                    segment.get_control_y2(),
                    segment.get_destination_x(),
                    segment.get_destination_y()
                )
            else:
                raise RuntimeError('Unsupported segment type: ' + strategy)

        if shape.get_is_closed():
            self._context.closePath()

        if current_machine.get_fill_enabled():
            self._context.fill()

        if current_machine.get_stroke_enabled():
            self._context.stroke()

    def draw_text(self, x: float, y: float, content: str):
        content = str(content)
        current_machine = self._get_current_state_machine()

        self._load_draw_params()
        self._load_font_params()

        if current_machine.get_fill_enabled():
            self._context.fillText(content, x, y)

        if current_machine.get_stroke_enabled():
            self._context.strokeText(content, x, y)

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
        return WebImage(src)

    def draw_image(self, x: float, y: float, image: sketchingpy.abstracted.Image):
        if not image.get_is_loaded():
            return

        self._load_draw_params()

        current_machine = self._get_current_state_machine()
        native_mode = current_machine.get_image_mode_native()
        mode_str = current_machine.get_image_mode_native()

        width = image.get_width()
        height = image.get_height()

        region = self._get_canvas_region_rect_like(x, y, width, height, native_mode, mode_str)

        self._context.drawImage(
            image.get_native(),
            region.get_x(),
            region.get_y(),
            region.get_width(),
            region.get_height()
        )

    def save_image(self, path: str):
        if not path.endswith('.png'):
            raise RuntimeError('Web export only supported to PNG.')

        link = js.document.createElement('a')
        link.download = path
        link.href = self._element.toDataURL('image/png')
        link.click()

    #########
    # State #
    #########

    def push_transform(self):
        self._context.save()

    def pop_transform(self):
        self._context.restore()

    ##########
    # System #
    ##########

    def get_native(self):
        return self._element

    def set_fps(self, rate: int):
        self._state_frame_rate = rate

    def set_title(self, title: str):
        js.document.title = title

    def quit(self):
        self._stopped = True

    def show(self, ax=None):
        self._show_internal(ax=ax, quit_immediately=False)

    def show_and_quit(self, ax=None):
        self._show_internal(ax=ax, quit_immediately=True)

    #############
    # Transform #
    #############

    def translate(self, x: float, y: float):
        self._context.translate(x, y)

    def rotate(self, angle: float):
        angle_rad = self._convert_to_radians(angle)
        self._context.rotate(angle_rad)

    def scale(self, scale: float):
        self._context.scale(scale, scale)

    ###########
    # Support #
    ###########

    def _show_internal(self, ax=None, quit_immediately=False):
        self._loading_element.style.display = 'none'
        self._element.style.display = 'inline-block'
        self._version = str(round(time.time()))
        self._element.setAttribute('version', self._version)

        for action in self._internal_pre_show_actions:
            action()

        if not quit_immediately:
            self._stopped = False

            self._last_render = time.time()
            self._internal_loop_callback = pyodide.ffi.create_proxy(lambda: self._inner_loop())

            self._inner_loop()

    def _inner_loop(self):
        if self._element.getAttribute('version') != self._version:
            self._stopped = True

        if self._stopped:
            if self._callback_quit is not None:
                self._callback_quit(self)
            return

        if self._callback_step is not None:
            self._callback_step(self)

        time_elapsed = (time.time() - self._last_render) * 1000
        time_delay = round(1000 / self._state_frame_rate - time_elapsed)

        js.setTimeout(self._internal_loop_callback, time_delay)

    def _create_state_machine(self):
        return PyscriptSketchStateMachine()

    def _get_canvas_region_arc_ellipse(self, x1: float, y1: float, x2: float,
        y2: float, mode_native: int, mode_str: str) -> CanvasRegionEllipse:
        if mode_native == sketchingpy.const.CENTER:
            center_x = x1
            center_y = y1
            radius_x = x2 / 2
            radius_y = y2 / 2
        elif mode_native == sketchingpy.const.RADIUS:
            center_x = x1
            center_y = y1
            radius_x = x2
            radius_y = y2
        elif mode_native == sketchingpy.const.CORNER:
            center_x = x1 + x2 / 2
            center_y = y1 + y2 / 2
            radius_x = x2 / 2
            radius_y = y2 / 2
        elif mode_native == sketchingpy.const.CORNERS:
            (x1, y1, x2, y2) = sketchingpy.abstracted.reorder_coords(x1, y1, x2, y2)
            width = x2 - x1
            height = y2 - y1
            center_x = x1 + width / 2
            center_y = y1 + height / 2
            radius_x = width / 2
            radius_y = height / 2
        else:
            raise RuntimeError('Unknown mode: ' + mode_str)

        return CanvasRegionEllipse(center_x, center_y, radius_x, radius_y)

    def _get_canvas_region_rect_like(self, x1: float, y1: float, x2: float,
        y2: float, native_mode: int, mode_str: str) -> CanvasRegionRect:
        if native_mode == sketchingpy.const.CENTER:
            start_x = x1 - x2 / 2
            start_y = y1 - y2 / 2
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
            width = 1 if x2 == 0 else x2
            height = 1 if y2 == 0 else y2
        elif native_mode == sketchingpy.const.CORNERS:
            (x1, y1, x2, y2) = sketchingpy.abstracted.reorder_coords(x1, y1, x2, y2)
            start_x = x1
            start_y = y1
            width = x2 - x1
            height = y2 - y1
        else:
            raise RuntimeError('Unknown mode: ' + mode_str)

        return CanvasRegionRect(start_x, start_y, width, height)

    def _load_draw_params(self):
        current_machine = self._get_current_state_machine()
        self._context.fillStyle = current_machine.get_fill_native()
        self._context.strokeStyle = current_machine.get_stroke_native()
        self._context.lineWidth = current_machine.get_stroke_weight_native()

    def _load_font_params(self):
        current_machine = self._get_current_state_machine()

        self._context.font = current_machine.get_text_font_native()

        text_align = current_machine.get_text_align_native()
        self._context.textAlign = text_align.get_horizontal_align()
        self._context.textBaseline = text_align.get_vertical_align()

    def _draw_arc_rad(self, x1: float, y1: float, x2: float, y2: float, a1: float, a2: float,
        mode_native: int, mode_str: str):
        self._load_draw_params()

        current_machine = self._get_current_state_machine()
        region = self._get_canvas_region_arc_ellipse(x1, y1, x2, y2, mode_native, mode_str)

        self._context.beginPath()

        self._context.ellipse(
            region.get_x(),
            region.get_y(),
            region.get_radius_x(),
            region.get_radius_y(),
            0,
            a1,
            a2
        )

        if current_machine.get_fill_enabled():
            self._context.fill()

        if current_machine.get_stroke_enabled():
            self._context.stroke()


class PyscriptSketchStateMachine(sketchingpy.state_struct.SketchStateMachine):
    """Implementation of SketchStateMachine for Pyscript types."""

    def __init__(self):
        """Create a new state machine for Pyscript-based sketches."""
        super().__init__()
        self._text_align_native = self._transform_text_align(super().get_text_align_native())

    def set_text_align(self, text_align: sketchingpy.state_struct.TextAlign):
        super().set_text_align(text_align)
        self._text_align_native = self._transform_text_align(super().get_text_align_native())

    def get_text_align_native(self):
        return self._text_align_native

    def get_text_font_native(self):
        return sketchingpy.abstracted.get_font_name(self.get_text_font(), os.path.sep)

    def _transform_text_align(self,
        text_align: sketchingpy.state_struct.TextAlign) -> sketchingpy.state_struct.TextAlign:

        HORIZONTAL_ALIGNS = {
            sketchingpy.const.LEFT: 'left',
            sketchingpy.const.CENTER: 'center',
            sketchingpy.const.RIGHT: 'right'
        }

        VERTICAL_ALIGNS = {
            sketchingpy.const.TOP: 'top',
            sketchingpy.const.CENTER: 'middle',
            sketchingpy.const.BASELINE: 'alphabetic',
            sketchingpy.const.BOTTOM: 'bottom'
        }

        return sketchingpy.state_struct.TextAlign(
            HORIZONTAL_ALIGNS[text_align.get_horizontal_align()],
            VERTICAL_ALIGNS[text_align.get_vertical_align()]
        )


class WebImage(sketchingpy.abstracted.Image):
    """Strategy implementation for HTML images."""

    def __init__(self, src: str):
        """Create a new image.

        Args:
            src: Path to the image.
        """
        super().__init__(src)

        image = js.document.createElement("img")
        image.src = src

        self._native = image
        self._width: typing.Optional[float] = None
        self._height: typing.Optional[float] = None

    def get_width(self) -> float:
        if self._width is None:
            return self._native.width
        else:
            return self._width

    def get_height(self) -> float:
        if self._height is None:
            return self._native.height
        else:
            return self._height

    def resize(self, width: float, height: float):
        self._width = width
        self._height = height

    def get_native(self):
        return self._native

    def get_is_loaded(self):
        return self._native.width > 0


class PyscriptMouse(sketchingpy.control_struct.Mouse):
    """Strategy implementation for Pyscript-based mouse access."""

    def __init__(self, element):
        """Create a new mouse strategy using HTML5.

        Args:
            element: The element to which mouse event listeners should be added.
        """
        self._element = element

        self._x = 0
        self._y = 0

        self._buttons_pressed = set()

        mouse_move_callback = pyodide.ffi.create_proxy(
            lambda event: self._report_mouse_move(event)
        )
        self._element.addEventListener(
            'mousemove',
            mouse_move_callback
        )

        mouse_down_callback = pyodide.ffi.create_proxy(
            lambda event: self._report_mouse_down(event)
        )
        self._element.addEventListener(
            'mousedown',
            mouse_down_callback
        )

        click_callback = pyodide.ffi.create_proxy(
            lambda event: self._report_click(event)
        )
        self._element.addEventListener(
            'click',
            click_callback
        )

        context_menu_callback = pyodide.ffi.create_proxy(
            lambda event: self._report_context_menu(event)
        )
        self._element.addEventListener(
            'contextmenu',
            context_menu_callback
        )

        self._press_callback = None
        self._release_callback = None

    def get_pointer_x(self):
        return self._x

    def get_pointer_y(self):
        return self._y

    def get_buttons_pressed(self) -> sketchingpy.control_struct.Buttons:
        return map(lambda x: sketchingpy.control_struct.Button(x), self._buttons_pressed)

    def on_button_press(self, callback: sketchingpy.control_struct.MouseCallback):
        self._press_callback = callback

    def on_button_release(self, callback: sketchingpy.control_struct.MouseCallback):
        self._release_callback = callback

    def _report_mouse_move(self, event):
        bounding_box = self._element.getBoundingClientRect()
        self._x = event.clientX - bounding_box.left
        self._y = event.clientY - bounding_box.top

    def _report_mouse_down(self, event):
        if event.button == 0:
            self._buttons_pressed.add(sketchingpy.const.MOUSE_LEFT_BUTTON)
            if self._press_callback is not None:
                button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_LEFT_BUTTON)
                self._press_callback(button)
        elif event.button == 2:
            self._buttons_pressed.add(sketchingpy.const.MOUSE_RIGHT_BUTTON)
            if self._press_callback is not None:
                button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_RIGHT_BUTTON)
                self._press_callback(button)

    def _report_click(self, event):
        self._buttons_pressed.remove(sketchingpy.const.MOUSE_LEFT_BUTTON)

        if self._release_callback is not None:
            button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_LEFT_BUTTON)
            self._release_callback(button)

        event.preventDefault()

    def _report_context_menu(self, event):
        self._buttons_pressed.remove(sketchingpy.const.MOUSE_RIGHT_BUTTON)

        if self._release_callback is not None:
            button = sketchingpy.control_struct.Button(sketchingpy.const.MOUSE_RIGHT_BUTTON)
            self._release_callback(button)

        event.preventDefault()


class PyscriptKeyboard(sketchingpy.control_struct.Keyboard):
    """Strategy implementation for Pyscript-based keyboard access."""

    def __init__(self, element):
        """Create a new mouse strategy using HTML5 and Pyscript.

        Args:
            element: The element to which keyboard event listeners should be added.
        """
        super().__init__()
        self._element = element
        self._pressed = set()
        self._press_callback = None
        self._release_callback = None

        keydown_callback = pyodide.ffi.create_proxy(
            lambda event: self._report_key_down(event)
        )
        self._element.addEventListener(
            'keydown',
            keydown_callback
        )

        keyup_callback = pyodide.ffi.create_proxy(
            lambda event: self._report_key_up(event)
        )
        self._element.addEventListener(
            'keyup',
            keyup_callback
        )

    def get_keys_pressed(self) -> sketchingpy.control_struct.Buttons:
        return map(lambda x: sketchingpy.control_struct.Button(x), self._pressed)

    def on_key_press(self, callback: sketchingpy.control_struct.KeyboardCallback):
        self._press_callback = callback

    def on_key_release(self, callback: sketchingpy.control_struct.KeyboardCallback):
        self._release_callback = callback

    def _report_key_down(self, event):
        key = self._map_key(event.key)

        if key is None:
            return

        self._pressed.add(key)

        if self._press_callback is not None:
            button = sketchingpy.control_struct.Button(key)
            self._press_callback(button)

        event.preventDefault()

    def _report_key_up(self, event):
        key = self._map_key(event.key)

        if key is None:
            return

        self._pressed.remove(key)

        if self._release_callback is not None:
            button = sketchingpy.control_struct.Button(key)
            self._release_callback(button)

        event.preventDefault()

    def _map_key(self, target: str) -> typing.Optional[str]:
        if target in KEY_MAP:
            return KEY_MAP[target]
        else:
            return target.lower()


class WebDataLayer(sketchingpy.data_struct.DataLayer):
    """Data layer which interfaces with network and browser."""

    def get_csv(self, path: str) -> sketchingpy.data_struct.Records:
        string_io = pyodide.http.open_url(path)
        reader = csv.DictReader(string_io)
        return list(reader)

    def write_csv(self, records: sketchingpy.data_struct.Records,
        columns: sketchingpy.data_struct.Columns, path: str):
        def build_record(target: typing.Dict) -> typing.Dict:
            return dict(map(lambda key: (key, target[key]), columns))

        records_serialized = map(build_record, records)

        target = io.StringIO()

        writer = csv.DictWriter(target, fieldnames=columns)  # type: ignore
        writer.writeheader()
        writer.writerows(records_serialized)

        self._download_text(target.getvalue(), path, 'text/csv')

    def get_json(self, path: str):
        string_io = pyodide.http.open_url(path)
        return json.loads(string_io.read())

    def write_json(self, target, path: str):
        self._download_text(json.dumps(target), path, 'application/json')

    def get_text(self, path: str):
        string_io = pyodide.http.open_url(path)
        return string_io.read()

    def write_text(self, target, path: str):
        self._download_text(target, path, 'text/plain')

    def _download_text(self, text: str, filename: str, mime: str):
        text_encoded = urllib.parse.quote(text)

        link = js.document.createElement('a')
        link.download = filename
        link.href = 'data:%s;charset=utf-8,%s' % (mime, text_encoded)

        link.click()


class WebDialogLayer(sketchingpy.dialog_struct.DialogLayer):
    """Dialog / simple UI layer for web apps."""

    def __init__(self, sketch: Sketch2DWeb):
        """"Initialize tkinter but hide the root window."""
        self._sketch = sketch

    def show_alert(self, message: str, callback: typing.Optional[typing.Callable[[], None]] = None):
        pyscript.window.alert(message)
        if callback is not None:
            callback()

    def show_prompt(self, message: str,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        response = pyscript.window.prompt(message)
        if callback is not None and response is not None:
            callback(response)

    def get_file_save_location(self,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        self.show_prompt('Filename to save:', callback)

    def get_file_load_location(self,
        callback: typing.Optional[typing.Callable[[str], None]] = None):
        self.show_prompt('Filename to load:', callback)
