echo "== [1 / 8] Preparing... =="
[ -e "website_build" ] && rm -r website_build
[ -e "self_host" ] && rm -r self_host
rm *.whl
mkdir website_build
mkdir website_build/community
mkdir website_build/guides
mkdir website_build/reference

echo "== [2 / 8] Rendering... =="
python3 support/render_website.py ./website_src/pages.yml ./website_src/reference.yml ./website_src ./website_build

echo "== [3 / 8] Building wheel... =="
mkdir website_build/dist
pip wheel .
chmod 644 *.whl
cp *.whl website_build/dist

echo "== [4 / 8] Moving assets... =="
cp -r website_src/css website_build/css
cp -r website_src/img website_build/img
cp -r website_src/js website_build/js
cp -r website_src/third_party website_build/third_party
cp -r website_src/third_party_site website_build/third_party_site

echo "== [5 / 8] Preparing examples... =="
cp -r examples website_build/examples
python3 support/update_version.py website_build/examples/web/example.html website_build/examples/web/example.html

echo "== [6 / 8] Building self-host... =="
cp -r website_src/third_party self_host
chmod 644 *.whl
mv *.whl self_host

echo "== [7 / 8] Packaging self-host... =="
zip -r self_host.zip self_host
mv self_host.zip website_build/dist

echo "== [8 / 8] Building pdoc =="
pdoc --docformat google ./sketchingpy -o website_build/devdocs/

echo "== Done! =="
