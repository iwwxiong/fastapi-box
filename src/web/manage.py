# -*-coding: utf-8 -*-

import sys
import logging
import importlib

from settings import settings

USAGE = (
    "manage.py COMMAND\n"
    "\n"
    "manage for tapparser"
    "\n"
    "\n"
    "Commands: \n"
    "\n"
    "\n"
    "manage.py COMMAND --help   see command help manual."
    "\n"
)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.getLevelName(settings.logger_level),
    format=settings.logger_formatter
)


def main():
    argv = sys.argv
    if len(argv) == 1 or (len(argv) == 2 and argv[1] in ("-h", "--help")):
        print(USAGE)
        sys.exit(-1)

    module = {
    }.get(argv[1], None)

    if module is None:
        print(USAGE)
        sys.exit(-1)

    mod = importlib.import_module('{}'.format(module))
    mod.run(sys.argv[2:])


if __name__ == "__main__":
    main()
