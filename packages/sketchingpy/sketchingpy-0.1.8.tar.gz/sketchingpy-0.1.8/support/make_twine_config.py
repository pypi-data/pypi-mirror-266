import os


def main():
    with open('pypirc', 'w') as f:
        f.write('[pypi]\n')
        f.write('username = __token__\n')
        f.write('password = %s\n' % os.environ['PYPI_TOKEN'])


if __name__ == '__main__':
    main()
