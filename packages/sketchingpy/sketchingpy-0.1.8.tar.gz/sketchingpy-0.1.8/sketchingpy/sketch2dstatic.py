"""Pillow-based renderer for Sketchingpy.

License:
    BSD
"""

import copy
import typing
import PIL.Image
import PIL.ImageColor
import PIL.ImageFont

has_matplot_lib = False
try:
    import matplotlib.pyplot
    has_matplot_lib = True
except:
    pass


has_numpy_lib = False
try:
    import numpy
    has_numpy_lib = True
except:
    pass

import sketchingpy.abstracted
import sketchingpy.const
import sketchingpy.control_struct
import sketchingpy.data_struct
import sketchingpy.local_data_struct
import sketchingpy.pillow_struct
import sketchingpy.pillow_util
import sketchingpy.state_struct
import sketchingpy.transform

DEFAULT_FPS = 20
MANUAL_OFFSET = False


class Sketch2DStatic(sketchingpy.abstracted.Sketch):
    """Pillow-based Sketch renderer."""

    def __init__(self, width: int, height: int, title: typing.Optional[str] = None,
        loading_src: typing.Optional[str] = None):
        """Create a new Pillow-based sketch.

        Args:
            width: The width of the sketch in pixels. This will be used as the horizontal image
                size.
            height: The height of the sketch in pixels. This will be used as the vertical image
                size.
            title: Title for the sketch. Ignored, reserved for future use.
            loading_src: ID for loading screen. Ignored, reserved for future use.
        """
        super().__init__()

        # System params
        self._width = width
        self._height = height

        # Internal image
        native_size = (self._width, self._height)
        target_image = PIL.Image.new('RGB', native_size)
        target_draw = PIL.ImageDraw.Draw(target_image, 'RGBA')

        self._target_writable = sketchingpy.pillow_struct.WritableImage(target_image, target_draw)
        self._base_writable = self._target_writable
        self._buffers: typing.Dict[str, sketchingpy.pillow_struct.WritableImage] = {}

        self._target_macro: typing.Optional[sketchingpy.pillow_struct.Macro] = None
        self._macros: typing.Dict[str, sketchingpy.pillow_struct.Macro] = {}
        self._in_macro = False

        # Other internals
        self._transformer = sketchingpy.transform.Transformer()
        self._transformer_stack: typing.List[sketchingpy.transform.Transformer] = []

    ##########
    # Buffer #
    ##########

    def create_buffer(self, name: str, width: int, height: int,
        background: typing.Optional[str] = None):
        if name in self._buffers:
            del self._buffers[name]

        if name in self._macros:
            del self._macros[name]

        has_alpha = self._get_is_color_transparent(background)
        if has_alpha:
            self._macros[name] = sketchingpy.pillow_struct.Macro(width, height)
        else:
            self._buffers[name] = self._make_buffer_surface(
                sketchingpy.pillow_struct.Rect(0, 0, width, height)
            )
            rect = (0, 0, width, height)
            self._buffers[name].get_drawable().rectangle(rect, fill=background, width=0)

    def enter_buffer(self, name: str):
        if name in self._buffers:
            self._target_writable = self._buffers[name]
            self._in_macro = False
        else:
            self._target_macro = self._macros[name]
            self._in_macro = True

    def exit_buffer(self):
        self._target_writable = self._base_writable
        self._in_macro = False

    def draw_buffer(self, x: float, y: float, name: str):
        if name in self._buffers:
            subject = self._buffers[name]
            transformed = self._get_transformed(subject.get_image(), x, y)
            self._draw_or_queue_transformed(transformed)
        elif name in self._macros:
            compiled = self._macros[name].get()
            moved = map(lambda piece: piece.get_with_offset(x, y), compiled)
            if self._in_macro:
                for piece in moved:
                    self._get_target_marco().append(piece)
            else:
                for piece in moved:
                    piece.draw(self._target_writable)
        else:
            raise RuntimeError('Unknown buffer: ' + name)

    ############
    # Controls #
    ############

    def get_keyboard(self) -> typing.Optional[sketchingpy.control_struct.Keyboard]:
        return None

    def get_mouse(self) -> typing.Optional[sketchingpy.control_struct.Mouse]:
        return None

    ########
    # Data #
    ########

    def get_data_layer(self) -> typing.Optional[sketchingpy.data_struct.DataLayer]:
        return sketchingpy.local_data_struct.LocalDataLayer()

    ###########
    # Dialogs #
    ###########

    def get_dialog_layer(self) -> typing.Optional[sketchingpy.dialog_struct.DialogLayer]:
        return None

    ###########
    # Drawing #
    ###########

    def clear(self, color_hex: str):
        color = PIL.ImageColor.getrgb(color_hex)
        transformed = sketchingpy.pillow_struct.TransformedClear(color)
        self._draw_or_queue_transformed(transformed)

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

        pillow_util_image = sketchingpy.pillow_util.make_arc_image(
            rect.get_x(),
            rect.get_y(),
            rect.get_width(),
            rect.get_height(),
            a1_rad,
            a2_rad,
            stroke_enabled,
            fill_enabled,
            stroke_native if stroke_enabled else None,
            fill_native if fill_enabled else None,
            stroke_weight
        )

        transformed = self._get_transformed(
            pillow_util_image.get_image(),
            pillow_util_image.get_x(),
            pillow_util_image.get_y()
        )

        self._draw_or_queue_transformed(transformed)

    def draw_ellipse(self, x1: float, y1: float, x2: float, y2: float):
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        mode_native = state_machine.get_ellipse_mode_native()
        rect = self._build_rect_with_mode(x1, y1, x2, y2, mode_native)

        pillow_util_image = sketchingpy.pillow_util.make_ellipse_image(
            rect.get_x(),
            rect.get_y(),
            rect.get_width(),
            rect.get_height(),
            stroke_enabled,
            fill_enabled,
            stroke_native,
            fill_native,
            stroke_weight
        )

        transformed = self._get_transformed(
            pillow_util_image.get_image(),
            pillow_util_image.get_x(),
            pillow_util_image.get_y()
        )

        self._draw_or_queue_transformed(transformed)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float):
        state_machine = self._get_current_state_machine()
        if not state_machine.get_stroke_enabled():
            return

        stroke_color = state_machine.get_stroke_native()
        stroke_weight = state_machine.get_stroke_weight_native()

        point_1 = self._transformer.transform(x1, y1)
        point_2 = self._transformer.transform(x2, y2)

        transformed = sketchingpy.pillow_struct.TransformedLine(
            point_1.get_x(),
            point_1.get_y(),
            point_2.get_x(),
            point_2.get_y(),
            stroke_color,
            stroke_weight * point_1.get_scale()
        )
        self._draw_or_queue_transformed(transformed)

    def draw_rect(self, x1: float, y1: float, x2: float, y2: float):
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        mode_native = state_machine.get_rect_mode_native()
        rect = self._build_rect_with_mode(x1, y1, x2, y2, mode_native)

        pillow_util_image = sketchingpy.pillow_util.make_rect_image(
            rect.get_x(),
            rect.get_y(),
            rect.get_width(),
            rect.get_height(),
            stroke_enabled,
            fill_enabled,
            stroke_native,
            fill_native,
            stroke_weight
        )

        transformed = self._get_transformed(
            pillow_util_image.get_image(),
            pillow_util_image.get_x(),
            pillow_util_image.get_y()
        )

        self._draw_or_queue_transformed(transformed)

    def draw_shape(self, shape: sketchingpy.shape_struct.Shape):
        if not shape.get_is_finished():
            raise RuntimeError('Finish your shape before drawing.')

        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        pillow_util_image = sketchingpy.pillow_util.make_shape_image(
            shape,
            stroke_enabled,
            fill_enabled,
            stroke_native if stroke_enabled else None,
            fill_native if fill_enabled else None,
            stroke_weight
        )

        transformed = self._get_transformed(
            pillow_util_image.get_image(),
            pillow_util_image.get_x(),
            pillow_util_image.get_y()
        )
        self._draw_or_queue_transformed(transformed)

    def draw_text(self, x: float, y: float, content: str):
        content = str(content)
        state_machine = self._get_current_state_machine()

        stroke_enabled = state_machine.get_stroke_enabled()
        fill_enabled = state_machine.get_fill_enabled()
        stroke_native = state_machine.get_stroke_native()
        fill_native = state_machine.get_fill_native()
        stroke_weight = state_machine.get_stroke_weight()

        text_font = state_machine.get_text_font_native()

        align_info = state_machine.get_text_align_native()
        anchor_str = align_info.get_horizontal_align() + align_info.get_vertical_align()

        pillow_util_image = sketchingpy.pillow_util.make_text_image(
            x,
            y,
            content,
            text_font,
            stroke_enabled,
            fill_enabled,
            stroke_native,
            fill_native,
            stroke_weight,
            anchor_str
        )

        transformed = self._get_transformed(
            pillow_util_image.get_image(),
            pillow_util_image.get_x(),
            pillow_util_image.get_y()
        )
        self._draw_or_queue_transformed(transformed)

    ##########
    # Events #
    ##########

    def on_step(self, callback: sketchingpy.abstracted.StepCallback):
        pass

    def on_quit(self, callback: sketchingpy.abstracted.QuitCallback):
        pass

    #########
    # Image #
    #########

    def get_image(self, src: str) -> sketchingpy.abstracted.Image:
        return PillowImage(src)

    def draw_image(self, x: float, y: float, image: sketchingpy.abstracted.Image):
        if not image.get_is_loaded():
            return

        image_mode_native = self._get_current_state_machine().get_image_mode_native()

        rect = self._build_rect_with_mode(
            x,
            y,
            image.get_width(),
            image.get_height(),
            image_mode_native
        )

        surface = image.get_native()

        transformed = self._get_transformed(surface, rect.get_x(), rect.get_y())
        self._draw_or_queue_transformed(transformed)

    def save_image(self, path: str):
        if self._in_macro:
            width = self._get_target_marco().get_width()
            height = self._get_target_marco().get_height()
            target = self._make_buffer_surface(sketchingpy.pillow_struct.Rect(0, 0, width, height))

            for compiled in self._get_target_marco().get():
                compiled.draw(target)

            target.get_image().save(path)
        else:
            self._target_writable.get_image().save(path)

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
        return self._target_writable

    def set_fps(self, rate: int):
        pass

    def set_title(self, title: str):
        pass

    def quit(self):
        pass

    def show(self, ax=None):
        if has_matplot_lib and has_numpy_lib:
            if ax is None:
                ax = matplotlib.pyplot.subplot(111)
                ax.axis('off')

            ax.imshow(numpy.asarray(self._target_writable.get_image()))
        else:
            raise RuntimeError('Install matplotlib and numpy or use save instead.')

    def show_and_quit(self, ax=None):
        pass

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

    def _get_target_marco(self) -> sketchingpy.pillow_struct.Macro:
        assert self._target_macro is not None
        return self._target_macro

    def _draw_or_queue_transformed(self,
        transformed: sketchingpy.pillow_struct.TransformedDrawable):
        if self._in_macro:
            self._get_target_marco().append(transformed)
        else:
            transformed.draw(self._target_writable)

    def _create_state_machine(self) -> sketchingpy.state_struct.SketchStateMachine:
        return PillowSketchStateMachine()

    def _make_buffer_surface(self,
        rect: sketchingpy.pillow_struct.Rect) -> sketchingpy.pillow_struct.WritableImage:
        native_size = (round(rect.get_width()), round(rect.get_height()))
        target_image = PIL.Image.new('RGB', native_size, (255, 255, 255, 0))
        target_draw = PIL.ImageDraw.Draw(target_image, 'RGBA')
        return sketchingpy.pillow_struct.WritableImage(target_image, target_draw)

    def _offset_stroke_weight(self, rect: sketchingpy.pillow_struct.Rect,
        stroke_weight: float) -> sketchingpy.pillow_struct.Rect:
        if not MANUAL_OFFSET:
            return rect

        half_weight = stroke_weight / 2
        return sketchingpy.pillow_struct.Rect(
            rect.get_x() - half_weight,
            rect.get_y() - half_weight,
            rect.get_width() + half_weight * 2,
            rect.get_height() + half_weight * 2
        )

    def _offset_fill_weight(self, rect: sketchingpy.pillow_struct.Rect,
        stroke_weight: float) -> sketchingpy.pillow_struct.Rect:
        if not MANUAL_OFFSET:
            return rect

        half_weight = stroke_weight / 2
        return sketchingpy.pillow_struct.Rect(
            rect.get_x() + half_weight,
            rect.get_y() + half_weight,
            rect.get_width() - half_weight * 2,
            rect.get_height() - half_weight * 2
        )

    def _zero_rect(self, rect: sketchingpy.pillow_struct.Rect) -> sketchingpy.pillow_struct.Rect:
        return sketchingpy.pillow_struct.zero_rect(rect)

    def _build_rect_with_mode(self, x1: float, y1: float, x2: float, y2: float,
        native_mode: int) -> sketchingpy.pillow_struct.Rect:
        return sketchingpy.pillow_struct.build_rect_with_mode(x1, y1, x2, y2, native_mode)

    def _get_transformed(self, surface: PIL.Image.Image, x: float,
        y: float) -> sketchingpy.pillow_struct.TransformedWritable:
        return sketchingpy.pillow_struct.get_transformed(
            self._transformer,
            surface,
            x,
            y
        )


class PillowSketchStateMachine(sketchingpy.state_struct.SketchStateMachine):

    def __init__(self):
        super().__init__()
        self._fill_native = self._convert_color(super().get_fill())
        self._stroke_native = self._convert_color(super().get_stroke())
        self._font_cache = {}
        self._text_align_native = self._transform_text_align(super().get_text_align_native())

    def set_fill(self, fill: str):
        super().set_fill(fill)
        self._fill_native = self._convert_color(super().get_fill())

    def get_fill_native(self):
        return self._fill_native

    def set_stroke(self, stroke: str):
        super().set_stroke(stroke)
        self._stroke_native = self._convert_color(super().get_stroke())

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

    def _convert_color(self, target: str) -> sketchingpy.pillow_struct.COLOR_TUPLE:
        return PIL.ImageColor.getrgb(target)


class PillowImage(sketchingpy.abstracted.Image):

    def __init__(self, src: str):
        super().__init__(src)
        self._native = PIL.Image.open(src)

    def get_width(self) -> float:
        return self._native.width

    def get_height(self) -> float:
        return self._native.height

    def resize(self, width: float, height: float):
        self._native = self._native.resize((int(width), int(height)))

    def get_native(self):
        return self._native

    def get_is_loaded(self):
        return True
