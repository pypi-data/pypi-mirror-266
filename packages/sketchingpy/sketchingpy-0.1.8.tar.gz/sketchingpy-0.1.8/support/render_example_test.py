import sys

NUM_ARGS = 3
USAGE_STR = 'USAGE: python render_example_test.py [pyscript] [template] [output]'


def main():
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    pyscript_loc = sys.argv[1]
    template_loc = sys.argv[2]
    output_loc = sys.argv[3]

    with open(pyscript_loc) as f:
        pyscript = f.read()

    with open(template_loc) as f:
        template = f.read()

    output_content = template.replace('{{ script }}', pyscript)

    with open(output_loc, 'w') as f:
        f.write(output_content)


if __name__ == '__main__':
    main()
