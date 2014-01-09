#!/usr/bin/python

import sys

try:
    import _preamble
except ImportError:
    pass

from mcl.main import main

if __name__ == "__main__":
    main()