import sys
import time

USAGE_STR = 'python update_version.py [src] [dest]'
NUM_ARGS = 2


def main():
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]

    with open(source) as f:
        source_contents = f.read()

    version = str(int(time.time()))
    destination_contents = source_contents.replace('{{ version }}', version)

    with open(destination, 'w') as f:
        f.write(destination_contents)


if __name__ == '__main__':
    main()
