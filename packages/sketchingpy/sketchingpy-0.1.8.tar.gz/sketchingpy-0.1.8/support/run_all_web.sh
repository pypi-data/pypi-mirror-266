[ -e "web_test_harness/dist/third_party" ] && rm -r web_test_harness/dist/third_party
cp -r website_build/third_party web_test_harness/third_party

[ -e "web_test_harness/dist/dist" ] && rm -r web_test_harness/dist/dist
cp -r website_build/dist web_test_harness/dist

cd web_test_harness
python3 -m http.server &
cd ..

python3 support/render_example_test.py examples/web/py/basics_state.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 1

python3 support/render_example_test.py examples/web/py/image_draw.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 2

python3 support/render_example_test.py examples/web/py/shapes_arc.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 3

python3 support/render_example_test.py examples/web/py/shapes_shape.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 4

python3 support/render_example_test.py examples/web/py/text_fill_stroke.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 5

python3 support/render_example_test.py examples/web/py/transform_combine.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 6

python3 support/render_example_test.py examples/web/py/geo_scale_transform.pyscript web_test_harness/template.html web_test_harness/example.html
python3 web_test_harness/run_harness.py || exit 7

