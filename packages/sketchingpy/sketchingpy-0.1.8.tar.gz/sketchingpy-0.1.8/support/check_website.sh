[ ! -e "website_build/index.html" ] && exit 1;
[ ! -e "website_build/community/code.html" ] && exit 2;
[ ! -e "website_build/css/base.css" ] && exit 3;
[ ! -e "website_build/examples/web/example.html" ] && exit 4;
[ ! -e "website_build/guides/start.html" ] && exit 5;
[ ! -e "website_build/img/issue.png" ] && exit 6;
[ ! -e "website_build/js/editor.js" ] && exit 7;
[ ! -e "website_build/third_party/core.js" ] && exit 8;
[ ! -e "website_build/third_party_site/ace.min.js" ] && exit 9;
[ ! -e "website_build/dist/self_host.zip" ] && exit 10;

echo "Website files found.";