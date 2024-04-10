#!/usr/bin/env python3

# Cast.py - dispatch FW jobs to HPC

import os

from .cluster import run_cast
from .util import frame


def main():
    print("CWD", os.getcwd())

    try:
        start = frame.timer()
        log = frame.log
        config = frame.run_cmd()

        if config:
            run_cast(start, config, log)

    except KeyboardInterrupt:
        frame.log.error("Aborted by Ctrl-C")


if __name__ == "__main__":  # pragma: no cover
    main()
