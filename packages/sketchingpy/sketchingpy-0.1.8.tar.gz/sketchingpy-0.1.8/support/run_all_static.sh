cd examples/static

[ -e "basics_state.png" ] && rm basics_state.png
python3 basics_state.py
[ ! -e "basics_state.png" ] && exit 1;
[ -e "../../website_build/img" ] && mv basics_state.png ../../website_build/img

[ -e "basics_styling.png" ] && rm basics_styling.png
python3 basics_styling.py
[ ! -e "basics_styling.png" ] && exit 2;
[ -e "../../website_build/img" ] && mv basics_styling.png ../../website_build/img

[ -e "data_read_csv.png" ] && rm data_read_csv.png
python3 data_read_csv.py
[ ! -e "data_read_csv.png" ] && exit 3;
[ -e "../../website_build/img" ] && mv data_read_csv.png ../../website_build/img

[ -e "data_read_json.png" ] && rm data_read_json.png
python3 data_read_json.py
[ ! -e "data_read_json.png" ] && exit 4;
[ -e "../../website_build/img" ] && mv data_read_json.png ../../website_build/img

[ -e "test.csv" ] && rm test.csv
python3 data_write_csv.py
[ ! -e "test.csv" ] && exit 5;

[ -e "test.json" ] && rm test.json
python3 data_write_json.py
[ ! -e "test.json" ] && exit 6;

[ -e "geo_geojson.png" ] && rm geo_geojson.png
python3 geo_geojson.py
[ ! -e "geo_geojson.png" ] && exit 7;
[ -e "../../website_build/img" ] && mv geo_geojson.png ../../website_build/img

[ -e "geo_polygon.png" ] && rm geo_polygon.png
python3 geo_polygon.py
[ ! -e "geo_polygon.png" ] && exit 7;
[ -e "../../website_build/img" ] && mv geo_polygon.png ../../website_build/img

[ -e "geo_scale_transform.png" ] && rm geo_scale_transform.png
python3 geo_scale_transform.py
[ ! -e "geo_scale_transform.png" ] && exit 7;
[ -e "../../website_build/img" ] && mv geo_scale_transform.png ../../website_build/img

[ -e "hello_static.png" ] && rm hello_static.png
python3 hello_static.py
[ ! -e "hello_static.png" ] && exit 7;
[ -e "../../website_build/img" ] && mv hello_static.png ../../website_build/img

[ -e "image_draw.png" ] && rm image_draw.png
python3 image_draw.py
[ ! -e "image_draw.png" ] && exit 8;
[ -e "../../website_build/img" ] && mv image_draw.png ../../website_build/img

[ -e "image_save.png" ] && rm image_save.png
python3 image_save.py
[ ! -e "image_save.png" ] && exit 9;
[ -e "../../website_build/img" ] && mv image_save.png ../../website_build/img

[ -e "shapes_arc.png" ] && rm shapes_arc.png
python3 shapes_arc.py
[ ! -e "shapes_arc.png" ] && exit 10;
[ -e "../../website_build/img" ] && mv shapes_arc.png ../../website_build/img

[ -e "shapes_bezier.png" ] && rm shapes_bezier.png
python3 shapes_bezier.py
[ ! -e "shapes_bezier.png" ] && exit 11;
[ -e "../../website_build/img" ] && mv shapes_bezier.png ../../website_build/img

[ -e "shapes_ellipse.png" ] && rm shapes_ellipse.png
python3 shapes_ellipse.py
[ ! -e "shapes_ellipse.png" ] && exit 12;
[ -e "../../website_build/img" ] && mv shapes_ellipse.png ../../website_build/img

[ -e "shapes_line.png" ] && rm shapes_line.png
python3 shapes_line.py
[ ! -e "shapes_line.png" ] && exit 13;
[ -e "../../website_build/img" ] && mv shapes_line.png ../../website_build/img

[ -e "shapes_rect.png" ] && rm shapes_rect.png
python3 shapes_rect.py
[ ! -e "shapes_rect.png" ] && exit 14;
[ -e "../../website_build/img" ] && mv shapes_rect.png ../../website_build/img

[ -e "shapes_shape.png" ] && rm shapes_shape.png
python3 shapes_shape.py
[ ! -e "shapes_shape.png" ] && exit 15;
[ -e "../../website_build/img" ] && mv shapes_shape.png ../../website_build/img

[ -e "text_fill_stroke.png" ] && rm text_fill_stroke.png
python3 text_fill_stroke.py
[ ! -e "text_fill_stroke.png" ] && exit 16;
[ -e "../../website_build/img" ] && mv text_fill_stroke.png ../../website_build/img

[ -e "text_horiz_align.png" ] && rm text_horiz_align.png
python3 text_horiz_align.py
[ ! -e "text_horiz_align.png" ] && exit 17;
[ -e "../../website_build/img" ] && mv text_horiz_align.png ../../website_build/img

[ -e "text_vert_align.png" ] && rm text_vert_align.png
python3 text_vert_align.py
[ ! -e "text_vert_align.png" ] && exit 18;
[ -e "../../website_build/img" ] && mv text_vert_align.png ../../website_build/img

[ -e "transform_combine.png" ] && rm transform_combine.png
python3 transform_combine.py
[ ! -e "transform_combine.png" ] && exit 19;
[ -e "../../website_build/img" ] && mv transform_combine.png ../../website_build/img

[ -e "transform_rotate.png" ] && rm transform_rotate.png
python3 transform_rotate.py
[ ! -e "transform_rotate.png" ] && exit 20;
[ -e "../../website_build/img" ] && mv transform_rotate.png ../../website_build/img

[ -e "transform_scale.png" ] && rm transform_scale.png
python3 transform_scale.py
[ ! -e "transform_scale.png" ] && exit 21;
[ -e "../../website_build/img" ] && mv transform_scale.png ../../website_build/img

[ -e "transform_state.png" ] && rm transform_state.png
python3 transform_state.py
[ ! -e "transform_state.png" ] && exit 22;
[ -e "../../website_build/img" ] && mv transform_state.png ../../website_build/img

[ -e "transform_translate.png" ] && rm transform_translate.png
python3 transform_translate.py
[ ! -e "transform_translate.png" ] && exit 23;
[ -e "../../website_build/img" ] && mv transform_translate.png ../../website_build/img


[ -e "buffer_simple.png" ] && rm buffer_simple.png
python3 buffer_simple.py
[ ! -e "buffer_simple.png" ] && exit 24;
[ -e "../../website_build/img" ] && mv buffer_simple.png ../../website_build/img

[ -e "buffer_opaque.png" ] && rm buffer_opaque.png
python3 buffer_opaque.py
[ ! -e "buffer_opaque.png" ] && exit 25;
[ -e "../../website_build/img" ] && mv buffer_opaque.png ../../website_build/img

[ -e "shapes_pixel.png" ] && rm shapes_pixel.png
python3 shapes_pixel.py
[ ! -e "shapes_pixel.png" ] && exit 26;
[ -e "../../website_build/img" ] && mv shapes_pixel.png ../../website_build/img
