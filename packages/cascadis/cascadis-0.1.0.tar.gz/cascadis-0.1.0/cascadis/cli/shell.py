#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import sys

from cascadis.environ import GlobalInterface

gi = GlobalInterface()


def main(_prog, _args):
    from IPython import start_ipython

    gi.setup_logging('INFO')
    start_ipython([], user_ns=globals())


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
