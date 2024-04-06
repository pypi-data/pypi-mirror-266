"""Interfaces for the strategies behind different rendering options.

License:
    BSD
"""

import copy
import math
import typing

import sketchingpy.const
import sketchingpy.control_struct
import sketchingpy.data_struct
import sketchingpy.dialog_struct
import sketchingpy.geo
import sketchingpy.shape_struct
import sketchingpy.state_struct

StepCallback = typing.Callable[['Sketch'], None]
QuitCallback = StepCallback


class Image:
    """Information about an image as an abstract base class."""

    def __init__(self, src: str):
        """Create a new image record.

        Args:
            src: The location from which the image was loaded.
        """
        self._src = src

    def get_src(self) -> str:
        """Get the location from which the image was loaded.

        Returns:
            Location for the image.
        """
        return self._src

    def get_width(self) -> float:
        """Get the width of this image in pixels.

        Returns:
            Horizontal width of this image.
        """
        raise NotImplementedError('Use implementor.')

    def get_height(self) -> float:
        """Get the height of this image in pixels.

        Returns:
            Vertical height of this image.
        """
        raise NotImplementedError('Use implementor.')

    def resize(self, width: float, height: float):
        """Resize this image by scaling.

        Args:
            width: The new desired width of this image in pixels.
            height: The new desired height of this image in pixels.
        """
        raise NotImplementedError('Use implementor.')

    def get_native(self):
        """Access the underlying native version of this image.

        Returns:
            Renderer specific native version.
        """
        raise NotImplementedError('Use implementor.')

    def get_is_loaded(self) -> bool:
        """Determine if this image has finished loading.

        Returns:
            True if loaded and ready to draw. False otherwise.
        """
        raise NotImplementedError('Use implementor.')


class Sketch:
    """Abstract base class for a sketch renderer strategy."""

    def __init__(self, width: typing.Optional[int] = None, height: typing.Optional[int] = None,
        title: typing.Optional[str] = None, loading_src: typing.Optional[str] = None):
        """Create a new sketch."""
        self._state_current_machine = self._create_state_machine()
        self._state_machine_stack: typing.List[sketchingpy.state_struct.SketchStateMachine] = []

        self._map_current_view = self._create_map_view()
        self._map_view_stack: typing.List[sketchingpy.geo.GeoTransformation] = []

    ##########
    # Buffer #
    ##########

    def create_buffer(self, name: str, width: int, height: int,
        background: typing.Optional[str] = None):
        """Create a new named in-memory (or equivalent) buffer.

        Args:
            name: The name of the buffer. If a prior buffer of this name exists, it will be
                replaced.
            width: The width of the buffer in pixels. In some renderers, the buffer will clip. In
                others, out of buffer values may be drawn.
            height: The height of the buffer in pixels. In some renderers, the buffer will clip. In
                others, out of buffer values may be drawn.
            background: The background to use for this buffer or None if transparent. Defaults to
                None.
        """
        raise NotImplementedError('Use implementor.')

    def enter_buffer(self, name: str):
        """Switch rendering context to a buffer, exiting current buffer if active.

        Args:
            name: The name of the buffer to which context should switch.
        """
        raise NotImplementedError('Use implementor.')

    def exit_buffer(self):
        """Exit the current offscreen buffer.

        Exit the current offscreen buffer, returning to the actual sketch. This will act as a noop
        if not currently in a buffer.
        """
        raise NotImplementedError('Use implementor.')

    def draw_buffer(self, x: float, y: float, name: str):
        """Draw an offscreen buffer to the current buffer or sketch.

        Args:
            x: The horizontal position in pixels at which the left should be drawn.
            y: The vertical position in pixels at which the top should be drawn.
            name: The name of the buffer to draw.
        """
        raise NotImplementedError('Use implementor.')

    ##########
    # Colors #
    ##########

    def set_fill(self, color_hex: str):
        """Set the fill color.

        Set the color to use for filling shapes and figures.

        Args:
            color_hex: Name of the color or a hex code.
        """
        self._get_current_state_machine().set_fill(color_hex)

    def clear_fill(self):
        """Clear the fill color.

        Set the fill color to fully transparent so that only outlines of shapes and figures are
        drawn.
        """
        self._get_current_state_machine().clear_fill()

    def set_stroke(self, color_hex: str):
        """Set the stroke color.

        Set the color to use for drawing outlines for shapes and figures as well as lines.

        Args:
            color_hex: Name of the color or a hex code.
        """
        self._get_current_state_machine().set_stroke(color_hex)

    def clear_stroke(self):
        """Clear the stroke color.

        Set the stroke width to zero, disabling the drawing of outlines for shapes and figures as
        well as lines.
        """
        self._get_current_state_machine().clear_stroke()

    ############
    # Controls #
    ############

    def get_keyboard(self) -> typing.Optional[sketchingpy.control_struct.Keyboard]:
        """Get access to the keyboard.

        Get access to the keyboard currently registered with the operating system for the sketch.
        Different sketches running at the same time may have different keyboards depending on focus
        or OS configuration.

        Returns:
            Current keyboard or None if not found / supported.
        """
        raise NotImplementedError('Use implementor.')

    def get_mouse(self) -> typing.Optional[sketchingpy.control_struct.Mouse]:
        """Get access to the mouse.

        Get access to the mouse currently registered with the operating system for the sketch.
        Different sketches running at the same time may have different mouse objects depending on
        focus or OS configuration. Note that the mouse may also be emulated if the device uses a
        touch screen.

        Returns:
            Current mouse or None if not found / supported.
        """
        raise NotImplementedError('Use implementor.')

    ########
    # Data #
    ########

    def get_data_layer(self) -> typing.Optional[sketchingpy.data_struct.DataLayer]:
        """Get access to reading and writing data.

        Open access to the file system, network, or browser to read or write data.

        Returns:
            Facade for data access or None if not supported or insufficient permissions.
        """
        raise NotImplementedError('Use implementor.')

    ###########
    # Dialogs #
    ###########

    def get_dialog_layer(self) -> typing.Optional[sketchingpy.dialog_struct.DialogLayer]:
        """Get access to rendering and using simple dialogs.

        Open access to a simple dialog prefabricated UI system to show alerts, prompts, and other
        dialog boxes.

        Returns:
            Facade for rendering dialogs or None if not supported or insufficient permissions.
        """
        raise NotImplementedError('Use implementor.')

    ###########
    # Drawing #
    ###########

    def clear(self, color: str):
        """Clear the sketch to a color.

        Peform the equivalent of drawing a rectangle the size of the sketch without stroke and with
        the given fill color.

        Args:
            color: The color to use in clearing.
        """
        raise NotImplementedError('Use implementor.')

    def set_arc_mode(self, mode: str):
        """Specify how Sketchingpy should interpret the position and size arguments for arcs.

        Determine how arcs should be placed within the sketch and how they should be sized.

        Args:
            mode: String describing the mode to use.
        """
        self._get_current_state_machine().set_arc_mode(mode)

    def draw_arc(self, x1: float, y1: float, x2: float, y2: float, a1: float, a2: float):
        """Draw a partial ellipse using starting and ending angles.

        Using starting and ending angles, draw a partial ellipse which is either drawn outside line
        only (stroke) and / or filled from the center of that ellipse.

        Args:
            x1: The x location at which to draw the arc.
            y1: The y location at which to draw the arc.
            x2: Horizontal size.
            y2: Vertical size.
            a1: Starting angle.
            a2: Ending angle.
        """
        raise NotImplementedError('Use implementor.')

    def set_ellipse_mode(self, mode: str):
        """Specify how Sketchingpy should interpret the position and size arguments.

        Determine how arcs should be placed within the sketch and how they should be sized for
        ellipses.

        Args:
            mode: String describing the mode to use.
        """
        self._get_current_state_machine().set_ellipse_mode(mode)

    def draw_ellipse(self, x1: float, y1: float, x2: float, y2: float):
        """Draw a circle or ellipse.

        Draw an ellipse or, in the case of equal width and height, a circle.

        Args:
            x1: The x location at which to draw the ellipse.
            y1: The y location at which to draw the ellipse.
            x2: Horizontal size.
            y2: Vertical size.
        """
        raise NotImplementedError('Use implementor.')

    def draw_line(self, x1: float, y1: float, x2: float, y2: float):
        """Draw a simple line.

        Draw a line between two points.

        Args:
            x1: The x coordinate from which the line should be drawn.
            y1: The y coordinate from which the line should be drawn.
            x2: The x coordinate to which the line should be drawn.
            y2: The y coordinate to which the line should be drawn.
        """
        raise NotImplementedError('Use implementor.')

    def set_rect_mode(self, mode: str):
        """Specify how Sketchingpy should interpret the position and size arguments.

        Determine how arcs should be placed within the sketch and how they should be sized for
        rectangles.

        Args:
            mode: String describing the mode to use.
        """
        self._get_current_state_machine().set_rect_mode(mode)

    def draw_rect(self, x1: float, y1: float, x2: float, y2: float):
        """Draw a rectangle.

        Draw a rectangle or, if width and height are the same, a square.

        Args:
            x1: The x location at which to draw the rectangle.
            y1: The y location at which to draw the rectangle.
            x2: Horizontal size.
            y2: Vertical size.
        """
        raise NotImplementedError('Use implementor.')

    def draw_pixel(self, x: float, y: float):
        """Draw a single pixel.

        Draw a rectangle with a width of zero and height of zero, changing a single pixel.

        Args:
            x: The x location at which to draw the rectangle.
            y: The y location at which to draw the rectangle.
        """
        self.push_style()
        self.set_rect_mode('corner')
        self.clear_stroke()
        self.draw_rect(x, y, 0, 0)
        self.pop_style()

    def start_shape(self, x: float, y: float) -> sketchingpy.shape_struct.Shape:
        """Create a new shape.

        Create a new shape which consists of multiple line or curve segments and which can be either
        open (stroke only) or closed (can be filled).

        Args:
            x: The starting x position of the shape.
            y: The starting y position of the shape.
        """
        return sketchingpy.shape_struct.Shape(x, y)

    def draw_shape(self, shape: sketchingpy.shape_struct.Shape):
        """Draw a shape.

        Draw a shape which consists of multiple line or curve segments and which can be either open
        (stroke only) or closed (can be filled).

        Args:
            shape: The shape to draw.
        """
        raise NotImplementedError('Use implementor.')

    def set_stroke_weight(self, weight: float):
        """Set the stroke color.

        Set the width of stroke for drawing outlines for shapes and figures as well as lines.

        Args:
            size: Number of pixels for the stroke weight.
        """
        self._get_current_state_machine().set_stroke_weight(weight)

    def set_text_font(self, identifier: str, size: float):
        """Set the type and size of text to draw.

        Set the size and font to use for drawing text.

        Args:
            font: Path to the TTF font file.
            size: Size of the font (px).
        """
        font = sketchingpy.state_struct.Font(identifier, size)
        self._get_current_state_machine().set_text_font(font)

    def set_text_align(self, horizontal_align: str, vertical_align: str = 'baseline'):
        """Indicate the alignment of text to be drawn.

        Indicate how the text should be aligned horizontally and vertically.

        Args:
            horizontal: Argument for horizontal alignment.
            vertical: Optional additional argument for vertical alignment. If not provided, will
                default to baseline.
        """
        align_struct = sketchingpy.state_struct.TextAlign(horizontal_align, vertical_align)
        self._get_current_state_machine().set_text_align(align_struct)

    def draw_text(self, x: float, y: float, content: str):
        """Draw text using the current font.

        Draw text using the current font and alignment.

        Args:
            x: The x coordinate at which to draw the text.
            y: The y coordinate at which to draw the text.
            text: The string to draw.
        """
        raise NotImplementedError('Use implementor.')

    ##########
    # Events #
    ##########

    def on_step(self, callback: StepCallback):
        """Callback for when the sketch ends execution.

        Register a callback for when the sketch redraws. This function should expect a single
        parameter which is the sketch redrawing.

        Args:
            callback: The function to invoke when the sketch stops execution.
        """
        raise NotImplementedError('Use implementor.')

    def on_quit(self, callback: QuitCallback):
        """Callback for when the sketch ends execution.

        Register a callback for when the sketch terminates.

        Args:
            callback: The function to invoke when the sketch stops execution.
        """
        raise NotImplementedError('Use implementor.')

    #######
    # Geo #
    #######

    def set_map_pan(self, longitude: float, latitude: float):
        """Indicate where point should be at the center of the map geographically.

        Indicate a latitude and longitude point which is where the map projection should be
        centerered geographically.

        Args:
            longitude: The center longitude in degrees.
            latitude: The center latitude in degrees.
        """
        self._map_current_view = sketchingpy.geo.GeoTransformation(
            sketchingpy.geo.GeoPoint(longitude, latitude),
            self._map_current_view.get_pixel_offset(),
            self._map_current_view.get_scale()
        )

    def set_map_zoom(self, zoom: float):
        """Indicate the map zoom level.

        Specify the map scaling factor or map "zoom" level.

        Args:
            zoom: The zoom level to use.
        """
        self._map_current_view = sketchingpy.geo.GeoTransformation(
            self._map_current_view.get_geo_offset(),
            self._map_current_view.get_pixel_offset(),
            zoom
        )

    def set_map_placement(self, x: float, y: float):
        """Indicate where in the sketch the map view should be drawn.

        Indicate where in the sketch in terms of pixel coordinates the map view should be centered
        such that the map pan latitude and longitude map to this coordinate position in pixel space.

        Args:
            x: The horizontal coordinate in pixels.
            y: The vertical coordinate in pixels.
        """
        self._map_current_view = sketchingpy.geo.GeoTransformation(
            self._map_current_view.get_geo_offset(),
            sketchingpy.geo.PixelOffset(x, y),
            self._map_current_view.get_scale()
        )

    def convert_geo_to_pixel(self, longitude: float,
        latitude: float) -> typing.Tuple[float, float]:
        """Convert a geographic location to a pixel coordinate.

        Convert a longitude / latitude coordinate pair in degrees to sketch coordinates in pixels
        using the current map view parameters.

        Args:
            longitude: The longitude to convert in degrees.
            latitude: The latitude to convert in degrees.

        Returns:
            Tuple with two elements: x coordinate and y coordinate.
        """
        point = sketchingpy.geo.GeoPoint(longitude, latitude, )
        x = point.get_x(transform=self._map_current_view)
        y = point.get_y(transform=self._map_current_view)
        return (x, y)

    def start_geo_polygon(self, longitude: float,
        latitude: float) -> sketchingpy.geo.GeoPolygonBuilder:
        """Start building a polygon using geographic coordinates.

        Start building a closed shape using geographic coordinates (longitude and latitude provided
        in degrees) instead of pixel coordinates.

        Args:
            longitude: The starting geographic point longitude coordinate or the E/W component of
                the first point of the polygon.
            latitude: The starting geographic point longitude coordinate or the N/S component of
                the first point of the polygon.

        Returns:
            Object to build geographic polygons.
        """
        get_current_view = lambda: self._map_current_view
        return sketchingpy.geo.GeoPolygonBuilder(longitude, latitude, get_current_view)

    def push_map(self):
        """Save current map view configuration.

        Save current map pan, zoom, and pixel placement to the map history. This works as a stack
        (like a stack of plates) where this puts a new plate on the top of the pile. This will leave
        the current map configuration in the sketch unchanged.
        """
        self._map_view_stack.append(self._map_current_view)

    def pop_map(self):
        """Restore a previously saved map view configuration.

        Restore the most recently saved map view configuration saved in style history, removing that
        config from the history. This works as a stack (like a stack of plates) where the top of
        the pile is taken off and restored, removing it from that stack. This will overwrite the
        current map view configuration in the sketch.
        """
        if len(self._map_view_stack) == 0:
            raise RuntimeError('Cannot pop an empty map view stack.')

        self._map_current_view = self._map_view_stack.pop()

    def parse_geojson(self, source: typing.Dict) -> typing.List[sketchingpy.geo.GeoPolygonBuilder]:
        """Utility to parse GeoJSON into a series of GeoPolygons.

        Utility to parse GeoJSON into a series of GeoPolygons which currently only supports
        MultiPolygon and Polygon.

        Args:
            source: The loaded GeoJSON source to parse.

        Returns:
            Polygon builder which can be converted to a shape.
        """
        raw_polygons = sketchingpy.geo.parse_geojson(source)
        return [self._build_geo_polygon_builder(polygon) for polygon in raw_polygons]

    #########
    # Image #
    #########

    def set_image_mode(self, mode: str):
        """Specify how Sketchingpy should place images.

        Determine how images' coordinates should be interpreted when drawing.

        Args:
            mode: String describing the mode to use.
        """
        self._get_current_state_machine().set_image_mode(mode)

    def get_image(self, src: str) -> Image:
        """Load an image file.

        Load an image from the local file system or URL.

        Args:
            src: The location from which the file should be read.
        """
        raise NotImplementedError('Use implementor.')

    def draw_image(self, x: float, y: float, image: Image):
        """Draw an image at a location.

        Draw a previously loaded image at a specific coordinate using its current size.

        Args:
            x: Horizontal coordinate at which to draw the image.
            y: Vertical coordinate at which to draw the image.
            image: The image to draw.
        """
        raise NotImplementedError('Use implementor.')

    def save_image(self, path: str):
        """Save an image file.

        Save the sketch as an image file, either directly to the file system or as a download.

        Args:
            path: The location at which the file should be written.
        """
        raise NotImplementedError('Use implementor.')

    ################
    # Other Params #
    ################

    def set_angle_mode(self, mode: str):
        """Indicate how angles should be provided to sketchingpy.

        Change the units with which angles are expressed to Sketchingpy in transforms and shapes.

        Args:
            mode: The units (either 'degrees' or 'radians') in which to supply angles.
        """
        self._get_current_state_machine().set_angle_mode(mode)

    #########
    # State #
    #########

    def push_transform(self):
        """Save current transformation state.

        Save current sketch transformation state to the matrix history. This works as a stack (like
        a stack of plates) where this puts a new plate on the top of the pile. This will leave the
        current transformation matrix in the sketch unchanged.
        """
        raise NotImplementedError('Use implementor.')

    def pop_transform(self):
        """Restore a previously saved transformation state.

        Restore the most recently transformation configuration saved in matrix history, removing
        that "transform matrix" from the history. This works as a stack (like a stack of plates)
        where the top of the pile is taken off and restored, removing it from that stack. This will
        overwrite the current transformation configuration in the sketch.
        """
        raise NotImplementedError('Use implementor.')

    def push_style(self):
        """Save current styling.

        Save current sketch styling to the style history. This works as a stack (like a stack of
        plates) where this puts a new plate on the top of the pile. This will leave the current
        style configuration in the sketch unchanged.
        """
        current = self._get_current_state_machine()
        current_copy = copy.deepcopy(current)
        self._state_machine_stack.append(current_copy)

    def pop_style(self):
        """Restore a previously saved styling.

        Restore the most recently saved styling configuration saved in style history, removing that
        styling from the history. This works as a stack (like a stack of plates) where the top of
        the pile is taken off and restored, removing it from that stack. This will overwrite the
        current style configuration in the sketch.
        """
        if len(self._state_machine_stack) == 0:
            raise RuntimeError('Cannot pop an empty style stack.')

        self._state_current_machine = self._state_machine_stack.pop()

    ##########
    # System #
    ##########

    def get_native(self):
        """Get a reference to the underlying native renderer object.

        Returns:
            Native render object.
        """
        raise NotImplementedError('Use implementor.')

    def quit(self):
        """Finish execution of the sketch.

        Cause the sketch to stop execution.
        """
        raise NotImplementedError('Use implementor.')

    def set_fps(self, rate: int):
        """Indicate how fast the sketch should redraw.

        Indicate a target frames per second that the sketch will take a "step" or redraw. Note that
        this is a goal and, if the system fall behind, it will drop frames and cause the on_step
        callback to be executed fewer times than the target.

        Args:
            rate: The number of frames to try to draw per second.
        """
        raise NotImplementedError('Use implementor.')

    def set_title(self, title: str):
        """Indicate the title to assign the window in the operating system.

        Indicate the human-readable string title to assign to the sketch window.

        Args:
            title: The text of the title.
        """
        raise NotImplementedError('Use implementor.')

    def show(self, ax=None):
        """Show the sketch.

        Show the sketch to the user and, if applicable, start the draw loop specified by set_fps.
        For Sketch2DApp, will execute any waiting drawing instructions provided to the sketch prior
        to showing. This is conceptually the same as "starting" the sketch.

        Args:
            ax: The container into which the sketch should be shown. Currently only supported for
                Sketch2DStatic. Optional and ignored on most renderers.
        """
        raise NotImplementedError('Use implementor.')

    def show_and_quit(self):
        """Show the sketch and quit immediatley afterwards.

        Show the sketch to the user and quit immediately afterwards, a routine potentially useful
        for testing.
        """
        raise NotImplementedError('Use implementor.')

    #############
    # Transform #
    #############

    def translate(self, x: float, y: float):
        """Change the location of the origin.

        Change the transform matrix such that any drawing afterwards is moved by a set amount.

        Args:
            x: The number of pixels to offset horizontally.
            y: The number of pixels to offset vertically.
        """
        raise NotImplementedError('Use implementor.')

    def rotate(self, angle: float):
        """Rotate around the current origin.

        Change the transform matrix such that any drawing afterwards is rotated around the current
        origin clock-wise.

        Args:
            angle: The angle by which to rotate.
        """
        raise NotImplementedError('Use implementor.')

    def scale(self, scale: float):
        """Scale outwards from the current origin.

        Change the transform matrix such that any drawing afterwards is scaled from the current
        origin.

        Args:
            scale: The factor by which to scale where values over 1 scale up and less than 1 scale
                down. A value of 1 will have no effect.
        """
        raise NotImplementedError('Use implementor.')

    ###########
    # Support #
    ###########

    def _get_is_color_transparent(self, target: typing.Optional[str]) -> bool:
        """Get if a color is transparent.

        Args:
            target: The color string to check if transparent. If None, assumes fully transparent.
                Also assumes named colors like "blue" are fully opaque.
        """
        if target is None:
            return True
        elif target.startswith('#') and len(target) > 7 and target[-2:] != 'FF':
            return True
        else:
            return False

    def _build_geo_polygon_builder(self,
        polygon: typing.List[typing.Tuple[float, float]]) -> sketchingpy.geo.GeoPolygonBuilder:
        get_current_view = lambda: self._map_current_view
        builder = sketchingpy.geo.GeoPolygonBuilder(polygon[0][0], polygon[0][1], get_current_view)

        for point in polygon[1:]:
            builder.add_coordinate(point[0], point[1])

        return builder

    def _convert_to_radians(self, angle: float) -> float:
        current_angle_mode = self._get_current_state_machine()

        if current_angle_mode == sketchingpy.const.RADIANS:
            return angle
        else:
            return math.radians(angle)

    def _create_map_view(self) -> sketchingpy.geo.GeoTransformation:
        return sketchingpy.geo.GeoTransformation(
            sketchingpy.geo.GeoPoint(sketchingpy.geo.BASE_LONGITUDE, sketchingpy.geo.BASE_LATITUDE),
            sketchingpy.geo.PixelOffset(sketchingpy.geo.BASE_X, sketchingpy.geo.BASE_Y),
            sketchingpy.geo.BASE_SCALE
        )

    def _create_state_machine(self) -> sketchingpy.state_struct.SketchStateMachine:
        raise NotImplementedError('Use implementor.')

    def _get_current_state_machine(self) -> sketchingpy.state_struct.SketchStateMachine:
        return self._state_current_machine


def reorder_coords(x1: float, y1: float, x2: float, y2: float) -> typing.List[float]:
    """Reorder coordinates so that the first comes before the second.

    Args:
        x1: The first x coordinate.
        y1: The first y coordinate.
        x2: The second x coordinate.
        y2: The second y coordinate.
    Returns:
        List of form [min_x, min_y, max_x, max_y].
    """
    x_coords = [x1, x2]
    y_coords = [y1, y2]
    x_coords.sort()
    y_coords.sort()
    return [x_coords[0], y_coords[0], x_coords[1], y_coords[1]]


def get_font_name(font, sep_char: str) -> str:
    """Get the web version of a font.

    Args:
        font: The font to convert to a web font identifier.
        sep_char: Path separator char.

    Returns:
        Web font identifier.
    """
    identifier = font.get_identifier()
    identifier = identifier.split(sep_char)[-1]

    if identifier.endswith('.ttf') or identifier.endswith('.otf'):
        identifier = identifier[:-4]

    return '%dpx %s' % (int(font.get_size()), identifier)
