import itertools
import os.path
import sys
import time

import jinja2
import yaml

NUM_ARGS = 4
REFERENCE_NAME = 'reference'
REFERENCE_TEMPLATE = 'reference_page.html'
TOC_TEMPLATE = 'toc.html'
USAGE_STR = 'USAGE: python render_website.py [pages yaml] [ref yaml] [templates] [output]'


def main():
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    # Parse args
    pages_loc = sys.argv[1]
    reference_loc = sys.argv[2]
    templates_loc = sys.argv[3]
    output_loc = sys.argv[4]

    # Load content
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_loc))

    with open(pages_loc) as f:
        pages = yaml.load(f.read(), Loader=yaml.CLoader)['pages']

    with open(reference_loc) as f:
        reference_info = yaml.load(f.read(), Loader=yaml.CLoader)

    version = int(time.time())

    # Main pages
    for page in pages:
        template = env.get_template(page['src'])
        rendered = template.render(
            sections=filter(lambda x: x.get('index', False), pages),
            current_section=page['section'],
            enable_pyscript=page.get('pyscript', False),
            title=page['label'],
            reference=reference_info if page.get('reference', False) else None,
            version=version
        )
        
        with open(os.path.join(output_loc, page['src']), 'w') as f:
            f.write(rendered)

    # Reference
    reference_sections = reference_info['sections']
    reference_pages = itertools.chain(*map(lambda x: x['items'], reference_sections))
    for page in reference_pages:
        template = env.get_template(REFERENCE_TEMPLATE)

        snippet_code = None
        if 'snippet' in page:
            snippet_code = '\n'.join(map(lambda x: x.strip(), page['snippet']['code'].split('\\n')))

        rendered = template.render(
            sections=filter(lambda x: x.get('index', False), pages),
            current_section=REFERENCE_NAME,
            enable_pyscript=False,
            title='Reference for ' + page['name'],
            reference_item=page,
            snippet_code= snippet_code,
            reference=reference_info
        )

        full_path = os.path.join(output_loc, 'reference', page['slug'] + '.html')
        with open(full_path, 'w') as f:
            f.write(rendered)

    # Table of contents
    reference_pages = itertools.chain(*map(lambda x: x['items'], reference_sections))
    toc_items = sorted(itertools.chain(
        map(lambda x: {'name': x['label'], 'url': x['url']}, pages),
        map(lambda x: {
            'name': 'Reference: ' + x['name'],
            'url': '/reference/' + x['slug'] + '.html'
        }, reference_pages)
    ), key=lambda x: x['name'])

    full_path = os.path.join(output_loc, 'toc.html')
    with open(full_path, 'w') as f:
        template = env.get_template(TOC_TEMPLATE)
        rendered = template.render(
            sections=filter(lambda x: x.get('index', False), pages),
            current_section='toc',
            enable_pyscript=False,
            title='Table of Contents',
            toc_items=toc_items
        )
        f.write(rendered)


if __name__ == '__main__':
    main()
