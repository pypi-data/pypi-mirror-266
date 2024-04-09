import os
import sys

from .gui.main import run


def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--run-gui':
        run()
    else:
        print("unknown arguments", file=sys.stderr)
        exit(-1)


if __name__ == "__main__":
    main()
