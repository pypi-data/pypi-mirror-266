cd examples

[ -e "local_temp" ] && rm -r local_temp
cp -r local local_temp
cd local_temp

sed -i -e 's/show/show_and_quit/g' basics_state.py
(xvfb-run -w 3 python3 basics_state.py) || exit 1

sed -i -e 's/show/show_and_quit/g' basics_styling.py
(xvfb-run -w 3 python3 basics_styling.py) || exit 2

sed -i -e 's/show/show_and_quit/g' data_read_csv.py
(xvfb-run -w 3 python3 data_read_csv.py) || exit 3

sed -i -e 's/show/show_and_quit/g' data_read_json.py
(xvfb-run -w 3 python3 data_read_json.py) || exit 4

sed -i -e 's/show/show_and_quit/g' data_write_csv.py
(xvfb-run -w 3 python3 data_write_csv.py) || exit 5

sed -i -e 's/show/show_and_quit/g' data_write_json.py
(xvfb-run -w 3 python3 data_write_json.py) || exit 6

sed -i -e 's/show/show_and_quit/g' geo_geojson.py
(xvfb-run -w 3 python3 geo_geojson.py) || exit 7

sed -i -e 's/show/show_and_quit/g' geo_polygon.py
(xvfb-run -w 3 python3 geo_polygon.py) || exit 9

sed -i -e 's/show/show_and_quit/g' geo_scale_transform.py
(xvfb-run -w 3 python3 geo_scale_transform.py) || exit 10

sed -i -e 's/show/show_and_quit/g' hello_homepage.py
(xvfb-run -w 3 python3 hello_homepage.py) || exit 11

sed -i -e 's/show/show_and_quit/g' hello_interactive.py
(xvfb-run -w 3 python3 hello_interactive.py) || exit 12

sed -i -e 's/show/show_and_quit/g' hello_static.py
(xvfb-run -w 3 python3 hello_static.py) || exit 13

sed -i -e 's/show/show_and_quit/g' image_draw.py
(xvfb-run -w 3 python3 image_draw.py) || exit 14

sed -i -e 's/show/show_and_quit/g' image_save.py
(xvfb-run -w 3 python3 image_save.py) || exit 15

sed -i -e 's/show/show_and_quit/g' inputs_keyboard.py
(xvfb-run -w 3 python3 inputs_keyboard.py) || exit 16

sed -i -e 's/show/show_and_quit/g' inputs_mouse.py
(xvfb-run -w 3 python3 inputs_mouse.py) || exit 17

sed -i -e 's/show/show_and_quit/g' shapes_arc.py
(xvfb-run -w 3 python3 shapes_arc.py) || exit 18

sed -i -e 's/show/show_and_quit/g' shapes_bezier.py
(xvfb-run -w 3 python3 shapes_bezier.py) || exit 19

sed -i -e 's/show/show_and_quit/g' shapes_ellipse.py
(xvfb-run -w 3 python3 shapes_ellipse.py) || exit 20

sed -i -e 's/show/show_and_quit/g' shapes_line.py
(xvfb-run -w 3 python3 shapes_line.py) || exit 21

sed -i -e 's/show/show_and_quit/g' shapes_rect.py
(xvfb-run -w 3 python3 shapes_rect.py) || exit 22

sed -i -e 's/show/show_and_quit/g' shapes_shape.py
(xvfb-run -w 3 python3 shapes_shape.py) || exit 23

sed -i -e 's/show/show_and_quit/g' text_fill_stroke.py
(xvfb-run -w 3 python3 text_fill_stroke.py) || exit 24

sed -i -e 's/show/show_and_quit/g' text_horiz_align.py
(xvfb-run -w 3 python3 text_horiz_align.py) || exit 25

sed -i -e 's/show/show_and_quit/g' text_vert_align.py
(xvfb-run -w 3 python3 text_vert_align.py) || exit 26

sed -i -e 's/show/show_and_quit/g' transform_combine.py
(xvfb-run -w 3 python3 transform_combine.py) || exit 27

sed -i -e 's/show/show_and_quit/g' transform_rotate.py
(xvfb-run -w 3 python3 transform_rotate.py) || exit 28

sed -i -e 's/show/show_and_quit/g' transform_scale.py
(xvfb-run -w 3 python3 transform_scale.py) || exit 29

sed -i -e 's/show/show_and_quit/g' transform_state.py
(xvfb-run -w 3 python3 transform_state.py) || exit 30

sed -i -e 's/show/show_and_quit/g' transform_translate.py
(xvfb-run -w 3 python3 transform_translate.py) || exit 31

sed -i -e 's/show/show_and_quit/g' buffer_simple.py
(xvfb-run -w 3 python3 buffer_simple.py) || exit 32

sed -i -e 's/show/show_and_quit/g' buffer_opaque.py
(xvfb-run -w 3 python3 buffer_opaque.py) || exit 3

sed -i -e 's/show/show_and_quit/g' shapes_pixel.py
(xvfb-run -w 3 python3 shapes_pixel.py) || exit 33

