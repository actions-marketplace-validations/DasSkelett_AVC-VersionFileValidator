#!/usr/bin/env python3.8

import os
from distutils.util import strtobool

from validator.utils import setup_logger
from validator.validator import validate_cwd


def validate_current_repository():
    debug = bool(strtobool(os.getenv('INPUT_DEBUG', 'false')))
    setup_logger(debug)

    exclude = os.getenv('INPUT_EXCLUDE', '')

    (status, successful, failed, ignored) = validate_cwd(exclude)
    print(f'Exiting with status {status}, {len(successful)} successful, {len(failed)} failed, {len(ignored)} ignored.')
    exit(status)


if __name__ == "__main__":
    validate_current_repository()
